import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import NtoPaper, NtoPaperForm, to_postgis_point, Georaphy, Nearest
from exceptions import NtoPaperNotFounded
from store.bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_nto_paper(
        record: Record,
        return_none: bool = False
) -> NtoPaper | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return NtoPaper.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise NtoPaperNotFounded


async def get_nto_paper(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> NtoPaper:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.nto_paper} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_nto_paper(record, return_none)


async def create_nto_paper(
        pool: asyncpg.Pool,
        form: NtoPaperForm,
) -> NtoPaper:
    sql = f"INSERT INTO {Tables.nto_paper} (" \
          f"id, address, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_nto_paper(record, False)


async def get_nearest_nto_paper(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.nto_paper,
        parse_func=_parse_nto_paper
    )


async def get_all_nto_paper(pool: asyncpg.Pool) -> list[NtoPaper]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.nto_paper}"
    return [_parse_nto_paper(x) for x in await pool.fetch(sql)]
