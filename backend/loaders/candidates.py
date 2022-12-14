import asyncio
import asyncpg
from contextlib import suppress
from misc.consts import BASE_CALCULATED_RADIUS

from models import CandidateType
from services import candidates as services
from store import get_all_mfc, get_all_libraries, get_all_parkings, \
    get_all_metro, get_all_houses, get_all_sports, get_all_culture_houses,\
    get_all_nto_paper, get_all_nto_non_paper, get_all_bus_stations, get_all_postamats, \
    get_all_loaded_candidates
from exceptions import *

import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)


async def load(pool: asyncpg.Pool):
    loaded = await get_all_loaded_candidates(pool)
    loaded = set(loaded)

    async def _load_type(objects, type: CandidateType):
        tasks = []
        loop = asyncio.get_event_loop()
        rows = len(objects)
        i = 0

        async def _load(obj):
            nonlocal i

            try:
                if (obj.point.lat, obj.point.lon, type) in loaded:
                    i += 1
                    if not i % 50 or rows - i > 5:
                        logging.info(f"SKIPPED CANDIDATES {type} {i / rows:.2%}")

                    return

                with suppress(DistrictNotFoundedError):
                    await services.calc_candidate(
                        pool=pool,
                        radius=BASE_CALCULATED_RADIUS,
                        point=obj.point,
                        type=type,
                        proto=obj
                    )

                loaded.add((obj.point.lat, obj.point.lon, type))
            except Exception as exc:
                logging.info(str(exc))

            i += 1
            if not i % 50 or rows - i > 5:
                logging.info(f"CALCULATED CANDIDATES {type} {i/rows:.2%}")

        for count, object in enumerate(objects, 1):
            if not count % 9:
                await asyncio.wait(tasks)
            #
            tasks.append(loop.create_task(_load(object)))
            # await _load(object)
        else:
            await asyncio.wait(tasks)

    for coro, type in zip([
        get_all_metro(pool),
        get_all_postamats(pool),
        get_all_mfc(pool),
        get_all_sports(pool),
        get_all_bus_stations(pool),
        get_all_culture_houses(pool),
        get_all_houses(pool),
        get_all_libraries(pool),
        get_all_nto_paper(pool),
        get_all_nto_non_paper(pool),
        get_all_parkings(pool),
    ], [
        CandidateType.metro,
        CandidateType.postamat,
        CandidateType.mfc,
        CandidateType.sports,
        CandidateType.bus_station,
        CandidateType.culture_house,
        CandidateType.house,
        CandidateType.library,
        CandidateType.nto_paper,
        CandidateType.nto_non_paper,
        CandidateType.parking,
    ]):
        objects = await coro
        logging.info(f"LOADING {type} CANDIDATES")
        await _load_type(objects, type)
