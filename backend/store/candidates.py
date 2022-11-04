import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import CandidateForm, Candidate, to_postgis_point, Georaphy, Nearest, to_postgis_poly, MapCandidate
from exceptions import CandidateNotFounded
from store.bases import get_nearest

SELECTION_STRING = '*, ST_X(point) as point_lat, ST_Y(point) as point_lon'
MAP_CANDIDATE_SELECTION_STRING = 'id, address, abbrev_ao, district_id, ' \
                                 'ST_X(point) as point_lat, ST_Y(point) as point_lon,' \
                                 'type, calculated_radius, modifier_v1, modifier_v2'

def _parse_candidate(
        record: Record,
        return_none: bool = False
) -> Candidate | None:
    if record:
        items = dict(record.items())
        items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
        return Candidate.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise CandidateNotFounded


def _parse_map_candidate(record: Record) -> MapCandidate:
    items = dict(record.items())
    items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))
    return MapCandidate.parse_obj(items)


async def get_candidate(
        pool: asyncpg.Pool,
        id: int,
        return_none: bool = False
) -> Candidate:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.candidates} WHERE id = $1"
    record = await pool.fetchrow(sql, id)

    return _parse_candidate(record, return_none)


async def get_candidate_by_point(
        pool: asyncpg.Pool,
        point: Georaphy,
        return_none: bool = False
) -> Candidate:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.candidates} WHERE point = $1"
    record = await pool.fetchrow(sql, to_postgis_point(point))

    return _parse_candidate(record, return_none)


async def create_candidate(
        pool: asyncpg.Pool,
        form: CandidateForm,
) -> Candidate:
    data = form.dict(exclude={'point'})
    insert_holders = ",".join(data.keys())
    value_holders = ",".join([f"${x+1}" for x in range(len(data.keys()))])
    point_holder = f'${len(data.keys()) + 1}'

    sql = f"INSERT INTO {Tables.candidates} ({insert_holders}, point) " \
          f"VALUES ({value_holders}, {point_holder}) RETURNING {SELECTION_STRING}"

    record = await pool.fetchrow(
        sql,
        *list(data.values()),
        to_postgis_point(form.point)
    )

    return _parse_candidate(record, False)


async def get_bbox_map_candidates(
        pool: asyncpg.Pool,
        poly: list[Georaphy]
) -> list[MapCandidate]:
    sql = f"SELECT {MAP_CANDIDATE_SELECTION_STRING} FROM {Tables.candidates} " \
          f"WHERE ST_CONTAINS($1, point)"
    records = await pool.fetch(sql, to_postgis_poly(poly))
    return [_parse_map_candidate(x) for x in records]


async def get_nearest_candidate(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float
) -> list[Nearest]:
    return await get_nearest(
        pool,
        point=point,
        max_radius=max_radius,
        selection_string=SELECTION_STRING,
        table=Tables.candidates,
        parse_func=_parse_candidate
    )
