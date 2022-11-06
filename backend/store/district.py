import asyncpg
from asyncpg import Record

from misc.db import Tables
from misc.tools import autocomplete
from models import DistrictForm, District, from_postgis_poly, \
    to_postgis_poly, to_postgis_point, Georaphy, DistrictAutocompleteObject, DistrictAutocompleteResponse, \
    DistrictFilter
from exceptions import DistrictNotFoundedError


SELECTION_STRING = 'id, abbrev_ao, name_ao, name, ST_AsText(polygon) as polygon, ' \
                   'ST_X(center) as center_lat, ST_Y(center) as center_lon, reliability'

def _parse_district(
        record: Record,
        return_none: bool = False
) -> District | None:
    if record:
        items = dict(record.items())

        items['polygon'] = from_postgis_poly(items['polygon'])
        items['center'] = Georaphy(lat=items.pop('center_lat'), lon=items.pop('center_lon'))

        return District.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise DistrictNotFoundedError


async def get_district(
        pool: asyncpg.Pool,
        id: int = None,
        name: str = None,
        return_none: bool = False
) -> District:
    if id:
        sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts} WHERE id = $1"
        record = await pool.fetchrow(sql, id)
    elif name:
        sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts} WHERE name = $1"
        record = await pool.fetchrow(sql, name)
    else:
        raise RuntimeError()

    return _parse_district(record, return_none)


async def create_district(
        pool: asyncpg.Pool,
        form: DistrictForm,
) -> District:
    sql = f"INSERT INTO {Tables.districts} (abbrev_ao, name_ao, name, polygon, center, reliability) " \
          f"VALUES ($1, $2, $3, $4, $5, $6) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.abbrev_ao,
        form.name_ao, form.name,
        to_postgis_poly(form.polygon),
        to_postgis_point(form.center),
        form.reliability
    )
    return _parse_district(record, False)


async def get_all_districts(pool: asyncpg.Pool) -> list[District]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts}"
    return [_parse_district(x) for x in await pool.fetch(sql)]


async def get_state_districts(pool: asyncpg.Pool, ao_abbrev: str) -> list[District]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts} WHERE abbrev_ao = $1"
    return [_parse_district(x) for x in await pool.fetch(sql, ao_abbrev)]


async def get_point_district(pool: asyncpg.Pool, point: Georaphy) -> District | None:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts} " \
          f"WHERE ST_CONTAINS(polygon, $1)"
    record = await pool.fetchrow(sql, to_postgis_point(point))
    return _parse_district(record, return_none=True)


async def get_bbox_districts(
        pool: asyncpg.Pool,
        filter: DistrictFilter
) -> list[District]:
    district_filter = ''
    if filter.districts_ids:
        district_filter = f" id IN ({','.join(map(str, filter.districts_ids))}) AND "

    sql = f"SELECT {SELECTION_STRING} FROM {Tables.districts} " \
          f"WHERE {district_filter} ST_INTERSECTS($1, polygon)"

    records = await pool.fetch(sql, to_postgis_poly(filter.to_poly()))

    return [_parse_district(x) for x in records]


async def autocomplete_districts(
        pool: asyncpg.Pool,
        query: str
) -> DistrictAutocompleteResponse:
    sql = f"SELECT id, name FROM {Tables.districts}"
    records = await pool.fetch(sql)

    all = [DistrictAutocompleteObject.parse_obj(dict(record)) for record in records]
    names = [x.name for x in all]
    keys = [x.id for x in all]

    result_ids = autocomplete(query, names, keys)

    return [
        DistrictAutocompleteObject(id=x.id, name=x.name.capitalize())
        for x in all if x.id in result_ids
    ]
