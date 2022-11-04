import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import LibraryForm, Library, to_postgis_point, Georaphy, Nearest
from exceptions import LibraryNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, modifier, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_library(
        record: Record,
        return_none: bool = False
) -> Library | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Library.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise LibraryNotFounded


async def get_library(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> Library:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.libraries} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_library(record, return_none)


async def create_library(
        pool: asyncpg.Pool,
        form: LibraryForm,
) -> Library:
    sql = f"INSERT INTO {Tables.libraries} (" \
          f"id, address, modifier, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        form.modifier,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_library(record, False)


async def get_nearest_libraries(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.libraries,
        parse_func=_parse_library
    )


async def get_all_libraries(pool: asyncpg.Pool) -> list[Library]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.libraries}"
    return [_parse_library(x) for x in await pool.fetch(sql)]
