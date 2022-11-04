import asyncio
import json
import asyncpg
from contextlib import suppress

from models import SportsForm, Georaphy
from store import sports as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

AVERAGE_WORK_HOURS = None


def calc_average_work_hours(data: list[dict]) -> float | None:
    total = 0
    count = 0

    for i in data:
        if i['DayWeek'] is None:
            continue

        hours = i['WorkHours']

        if hours.lower().strip() == 'закрыто':
            count += 1
            total += 0
            continue
        elif hours.lower().strip() == 'круглосуточно':
            count += 1
            total += 24
            continue

        left, right = hours.split('-')
        left = left.split(':')
        right = right.split(':')

        if right[0] > left[0]:
            total += (int(right[0]) + int(right[1]) / 60) - (int(left[0]) + int(left[1]) / 60)
        else:
            total += 24 + (int(right[0]) + int(right[1]) / 60) - (int(left[0]) + int(left[1]) / 60)
        count += 1

    try:
        return total / count
    except ZeroDivisionError:
        return None


async def load(pool: asyncpg.Pool):
    with open('/datasets/data_src/sport_facilities.json') as file:
        sports = json.load(file)

    count_work_hours = 0
    total_work_hours = 0

    for obj in sports['features']:
        attrs = obj['properties']['Attributes']
        work_hours = calc_average_work_hours(attrs['WorkingHours'])
        if work_hours:
            total_work_hours += work_hours
            count_work_hours += 1

    rows = len(sports['features'])

    AVERAGE_WORK_HOURS = total_work_hours / count_work_hours

    i = 0

    async def _load(obj):
        nonlocal i

        props = obj['properties']
        attrs = props['Attributes']

        id = attrs['global_id']
        work_hours = calc_average_work_hours(attrs['WorkingHours']) or AVERAGE_WORK_HOURS / 1.25

        point = Georaphy(
            lat=float(obj['geometry']['coordinates'][0][1]),
            lon=float(obj['geometry']['coordinates'][0][0])
        )

        district = await get_point_district(pool, point)

        if not district:
            i += 1
            return

        try:
            address = attrs['ObjectAddress'][0]['Address']
        except IndexError:
            address = f'г Москва, {district.abbrev_ao}, {district.name}'

        with suppress(asyncpg.UniqueViolationError):
            await store.create_sports(
                pool, form=SportsForm(
                    id=id,
                    address=address,
                    modifier=work_hours/24,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    point=point
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED SPORTS {i/rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in sports['features']:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
