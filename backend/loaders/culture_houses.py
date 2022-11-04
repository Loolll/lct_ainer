import asyncio
import json
import asyncpg
from contextlib import suppress

from models import CultureHouseForm, Georaphy
from store import culture_house as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)


async def load(pool: asyncpg.Pool):
    with open('/datasets/data_src/culture_house.json') as file:
        culture_houses = json.load(file)

    rows = len(culture_houses['features'])

    i = 0

    async def _load(house):
        nonlocal i

        props = house['properties']
        attrs = props['Attributes']

        id = attrs['global_id']
        point = Georaphy(
            lat=float(house['geometry']['coordinates'][0][1]),
            lon=float(house['geometry']['coordinates'][0][0])
        )
        address = attrs['ShortName']

        district = await get_point_district(pool, point)
        if not district:
            i += 1
            return

        with suppress(asyncpg.UniqueViolationError):
            await store.create_culture_house(
                pool, form=CultureHouseForm(
                    id=id,
                    address=address,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    point=point
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED CULTURE HOUSES {i/rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in culture_houses['features']:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
