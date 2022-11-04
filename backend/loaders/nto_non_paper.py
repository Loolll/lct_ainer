import asyncio
import json
import asyncpg
from contextlib import suppress

from models import NtoNonPaperForm, Georaphy
from store import nto_non_paper as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)


async def load(pool: asyncpg.Pool):
    with open('/datasets/data_src/nto_non_paper.json') as file:
        nto_paper = json.load(file)

    rows = len(nto_paper['features'])

    i = 0

    async def _load(obj):
        nonlocal i

        props = obj['properties']
        attrs = props['Attributes']

        if attrs['ContractStatus'].lower().strip() != 'действует':
            i += 1
            return

        id = attrs['global_id']
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
            await store.create_nto_non_paper(
                pool, form=NtoNonPaperForm(
                    id=id,
                    address=address,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    point=point
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED NTO NON PAPER {i/rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in nto_paper['features']:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
