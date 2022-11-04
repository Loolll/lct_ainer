import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import MetroForm, Metro, to_postgis_point, Georaphy, Nearest
from exceptions import MetroNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, station, entrance, district_id, ' \
                   'abbrev_ao, ST_X(point) as point_lat, ST_Y(point) as point_lon, traffic_modifier'

def _parse_metro(
        record: Record,
        return_none: bool = False
) -> Metro | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Metro.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise MetroNotFounded


async def get_metro(
        pool: asyncpg.Pool,
        id: int = None,
        station: str = None,
        return_none: bool = False
) -> Metro:
    if id:
        sql = f"SELECT {SELECTION_STRING} FROM {Tables.metro} WHERE id = $1"
        record = await pool.fetchrow(sql, id)
    elif station:
        sql = f"SELECT {SELECTION_STRING} FROM {Tables.metro} WHERE station = $1"
        record = await pool.fetchrow(sql, station)
    else:
        raise RuntimeError

    return _parse_metro(record, return_none)


async def create_metro(
        pool: asyncpg.Pool,
        form: MetroForm,
) -> Metro:
    sql = f"INSERT INTO {Tables.metro} (" \
          f"station, entrance, district_id, " \
          f"abbrev_ao, point, traffic_modifier" \
          f") " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql,
        form.station, form.entrance,
        form.district_id, form.abbrev_ao,
        to_postgis_point(form.point),
        form.traffic_modifier
    )
    return _parse_metro(record, False)


async def get_nearest_metro(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.metro,
        parse_func=_parse_metro
    )


async def get_all_metro(pool: asyncpg.Pool) -> list[Metro]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.metro}"
    return [_parse_metro(x) for x in await pool.fetch(sql)]
