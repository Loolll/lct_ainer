import asyncio
import json
import asyncpg
from contextlib import suppress

from models import MfcForm, Georaphy
from store import mfc as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

AVERAGE_WINDOWS = None
MAX_WINDOWS = 0


async def load(pool: asyncpg.Pool):
    global MAX_WINDOWS, AVERAGE_WINDOWS

    with open('/datasets/data_src/mfc.json') as file:
        mfc = json.load(file)

    count_windows = 0
    total_windows = 0

    for obj in mfc['features']:
        attrs = obj['properties']['Attributes']
        if attrs['WindowCount'] is not None:
            total_windows += attrs['WindowCount']
            MAX_WINDOWS = max(MAX_WINDOWS, attrs['WindowCount'])
            count_windows += 1

    rows = len(mfc['features'])

    AVERAGE_WINDOWS = total_windows / count_windows

    i = 0

    async def _load(obj):
        nonlocal i

        props = obj['properties']
        attrs = props['Attributes']

        id = attrs['global_id']
        windows = attrs['WindowCount'] or AVERAGE_WINDOWS / 1.5

        point = Georaphy(
            lat=float(obj['geometry']['coordinates'][1]),
            lon=float(obj['geometry']['coordinates'][0])
        )
        address = attrs['Address']

        district = await get_point_district(pool, point)

        if not district:
            i += 1
            return

        with suppress(asyncpg.UniqueViolationError):
            await store.create_mfc(
                pool, form=MfcForm(
                    id=id,
                    address=address,
                    modifier=windows/MAX_WINDOWS,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    point=point
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED MFC {i/rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in mfc['features']:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
