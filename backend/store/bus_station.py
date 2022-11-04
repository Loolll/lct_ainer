import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import BusStationForm, BusStation, to_postgis_point, Georaphy, Nearest
from exceptions import BusStationNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, district_id, abbrev_ao, modifier, address, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_bus_station(
        record: Record,
        return_none: bool = False
) -> BusStation | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return BusStation.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise BusStationNotFounded


async def get_bus_station(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> BusStation:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.bus_stations} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_bus_station(record, return_none)


async def create_bus_station(
        pool: asyncpg.Pool,
        form: BusStationForm,
) -> BusStation:
    sql = f"INSERT INTO {Tables.bus_stations} (" \
          f"id, address, modifier, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        form.modifier,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_bus_station(record, False)


async def get_nearest_bus_stations(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.bus_stations,
        parse_func=_parse_bus_station
    )


async def get_all_bus_stations(pool: asyncpg.Pool) -> list[BusStation]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.bus_stations}"
    return [_parse_bus_station(x) for x in await pool.fetch(sql)]
