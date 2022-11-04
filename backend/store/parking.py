import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import ParkingForm, Parking, to_postgis_point, Georaphy, Nearest
from exceptions import ParkingNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, size_modifier, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_parking(
        record: Record,
        return_none: bool = False
) -> Parking | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Parking.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise ParkingNotFounded


async def get_parking(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> Parking:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.parking} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_parking(record, return_none)


async def create_parking(
        pool: asyncpg.Pool,
        form: ParkingForm,
) -> Parking:
    sql = f"INSERT INTO {Tables.parking} (" \
          f"id, address, size_modifier, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        form.size_modifier,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_parking(record, False)


async def get_nearest_parkings(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.parking,
        parse_func=_parse_parking
    )


async def get_all_parkings(pool: asyncpg.Pool) -> list[Parking]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.parking}"
    return [_parse_parking(x) for x in await pool.fetch(sql)]
