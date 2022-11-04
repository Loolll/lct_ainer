from misc.db import get_db

from .states import load as load_states
from .districts import load as load_districts
from .metro import load as load_metro
from .postamats import load as load_postamat
from .parking import load as load_parking
from .bus_stations import load as load_bus_stations
from .culture_houses import load as load_culture_house
from .libraries import load as load_libraries
from .mfc import load as load_mfc
from .sports import load as load_sports
from .nto_paper import load as load_nto_paper
from .nto_non_paper import load as load_nto_non_paper

from .candidates import load as load_candidates

async def main():
    pool = await get_db()

    # await load_states(pool)
    # await load_districts(pool)
    # await load_metro(pool)
    # await load_postamat(pool)
    # await load_parking(pool)
    # await load_bus_stations(pool)
    # await load_culture_house(pool)
    # await load_libraries(pool)
    # await load_sports(pool)
    # await load_nto_paper(pool)
    # await load_nto_non_paper(pool)
    # await load_mfc(pool)

    # TODO reload! without 1000 limit
    # from .houses import load as load_houses
    # await load_houses(pool)

    await load_candidates(pool)
