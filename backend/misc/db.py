import asyncpg
import os
from enum import Enum

db = None


async def get_db() -> asyncpg.Pool:
    global db
    if not db:
        db = await asyncpg.create_pool(
            os.getenv('DB_DEST')
        )

    return db


class Tables(str, Enum):
    states = 'states'
    districts = 'districts'
    metro = 'metro'
    postamats = 'postamats'
    parking = 'parking'
    bus_stations = 'bus_stations'
    culture_houses = 'culture_houses'
    libraries = 'libraries'
    mfc = 'mfc'
    sports = 'sports'
    nto_paper = 'nto_paper'
    nto_non_paper = 'nto_non_paper'
    houses = 'houses'
    candidates = 'candidates'
