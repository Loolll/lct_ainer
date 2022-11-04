import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import Sports, SportsForm, to_postgis_point, Georaphy, Nearest
from exceptions import SportsNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, modifier, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_sports(
        record: Record,
        return_none: bool = False
) -> Sports | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Sports.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise SportsNotFounded


async def get_sports(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> Sports:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.sports} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_sports(record, return_none)


async def create_sports(
        pool: asyncpg.Pool,
        form: SportsForm,
) -> Sports:
    sql = f"INSERT INTO {Tables.sports} (" \
          f"id, address, modifier, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        form.modifier,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_sports(record, False)


async def get_nearest_sports(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.sports,
        parse_func=_parse_sports
    )


async def get_all_sports(pool: asyncpg.Pool) -> list[Sports]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.sports}"
    return [_parse_sports(x) for x in await pool.fetch(sql)]
