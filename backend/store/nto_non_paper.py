import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import NtoNonPaper, NtoNonPaperForm, Nearest, to_postgis_point, Georaphy
from exceptions import NtoNonPaperNotFounded
from .bases import get_nearest

SELECTION_STRING = 'id, address, district_id, abbrev_ao, ' \
                   'ST_X(point) as point_lat, ST_Y(point) as point_lon'


def _parse_nto_non_paper(
        record: Record,
        return_none: bool = False
) -> NtoNonPaper | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return NtoNonPaper.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise NtoNonPaperNotFounded


async def get_nto_non_paper(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> NtoNonPaper:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.nto_non_paper} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_nto_non_paper(record, return_none)


async def create_nto_non_paper(
        pool: asyncpg.Pool,
        form: NtoNonPaperForm,
) -> NtoNonPaper:
    sql = f"INSERT INTO {Tables.nto_non_paper} (" \
          f"id, address, point, abbrev_ao, district_id) " \
          f"VALUES ($1, $2, $3, $4, $5) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.id,
        form.address,
        to_postgis_point(form.point),
        form.abbrev_ao, form.district_id
    )

    return _parse_nto_non_paper(record, False)


async def get_nearest_nto_non_paper(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.nto_non_paper,
        parse_func=_parse_nto_non_paper
    )


async def get_all_nto_non_paper(pool: asyncpg.Pool) -> list[NtoNonPaper]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.nto_non_paper}"
    return [_parse_nto_non_paper(x) for x in await pool.fetch(sql)]
