import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import CultureHouseForm, CultureHouse, to_postgis_point, Georaphy, Nearest
from exceptions import CultureHouseNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_culture_house(
        record: Record,
        return_none: bool = False
) -> CultureHouse | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return CultureHouse.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise CultureHouseNotFounded


async def get_culture_house(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> CultureHouse:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.culture_houses} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_culture_house(record, return_none)


async def create_culture_house(
        pool: asyncpg.Pool,
        form: CultureHouseForm,
) -> CultureHouse:
    sql = f"INSERT INTO {Tables.culture_houses} (" \
          f"id, address, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_culture_house(record, False)


async def get_nearest_culture_houses(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.culture_houses,
        parse_func=_parse_culture_house
    )


async def get_all_culture_houses(pool: asyncpg.Pool) -> list[CultureHouse]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.culture_houses}"
    return [_parse_culture_house(x) for x in await pool.fetch(sql)]
