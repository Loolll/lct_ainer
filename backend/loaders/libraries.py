import asyncio
import json
import asyncpg
from contextlib import suppress

from models import LibraryForm, Georaphy
from store import libraries as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

AVERAGE_VISITORS = None
MAX_VISITORS = 0


async def load(pool: asyncpg.Pool):
    global AVERAGE_VISITORS, MAX_VISITORS

    with open('/datasets/data_src/libraries.json') as file:
        libraries = json.load(file)

    count_visitors = 0
    total_visitors = 0

    for obj in libraries['features']:
        attrs = obj['properties']['Attributes']
        if attrs['NumOfVisitors'] is not None:
            total_visitors += attrs['NumOfVisitors']
            MAX_VISITORS = max(MAX_VISITORS, attrs['NumOfVisitors'])
            count_visitors += 1

    rows = len(libraries['features'])

    AVERAGE_VISITORS = total_visitors / count_visitors

    i = 0

    async def _load(obj):
        nonlocal i

        props = obj['properties']
        attrs = props['Attributes']

        id = attrs['global_id']
        visitors = attrs['NumOfVisitors'] or AVERAGE_VISITORS / 1.5

        point = Georaphy(
            lat=float(obj['geometry']['coordinates'][0][1]),
            lon=float(obj['geometry']['coordinates'][0][0])
        )
        address = attrs['ShortName']

        district = await get_point_district(pool, point)

        if not district:
            i += 1
            return

        with suppress(asyncpg.UniqueViolationError):
            await store.create_library(
                pool, form=LibraryForm(
                    id=id,
                    address=address,
                    modifier=visitors/MAX_VISITORS,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    point=point
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED LIBRARIES {i/rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in libraries['features']:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
