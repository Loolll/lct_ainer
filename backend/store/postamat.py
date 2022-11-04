import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import PostamatForm, Postamat, to_postgis_point, Georaphy, Nearest
from exceptions import PostamatNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, company, address, hours_modifier, company_modifier, district_id, abbrev_ao, metro_id, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon, result_modifier'


def _parse_postamat(
        record: Record,
        return_none: bool = False
) -> Postamat | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Postamat.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise PostamatNotFounded


async def get_postamat(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> Postamat:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.postamats} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_postamat(record, return_none)


async def create_postamat(
        pool: asyncpg.Pool,
        form: PostamatForm,
) -> Postamat:
    sql = f"INSERT INTO {Tables.postamats} (" \
          f"id, company, address, hours_modifier, " \
          f"company_modifier, result_modifier, point, abbrev_ao, district_id, metro_id) " \
          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.company, form.address,
        form.hours_modifier,
        form.company_modifier, form.result_modifier,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id,
        form.metro_id
    )

    return _parse_postamat(record, False)


async def get_nearest_postamats(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.postamats,
        parse_func=_parse_postamat
    )


async def get_all_postamats(pool: asyncpg.Pool) -> list[Postamat]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.postamats}"
    return [_parse_postamat(x) for x in await pool.fetch(sql)]
