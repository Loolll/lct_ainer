import asyncpg
from asyncpg import Record

from misc.db import Tables
from misc.colors import get_color_grad
from misc.consts import MAX_SCREEN_CANDIDATES, BASE_CALCULATED_RADIUS
from models import CandidateForm, Candidate, \
    to_postgis_point, Georaphy, Nearest, \
    to_postgis_poly, MapCandidate, CandidateFilter, CandidateType
from exceptions import CandidateNotFounded
from store.bases import get_nearest

SELECTION_STRING = '*, ST_X(point) as point_lat, ST_Y(point) as point_lon'
MAP_CANDIDATE_SELECTION_STRING = 'id, address, abbrev_ao, district_id, ' \
                                 'ST_X(point) as point_lat, ST_Y(point) as point_lon,' \
                                 'type, calculated_radius, modifier_v1, modifier_v2'
AGGREGATE_MAP_CANDIDATE_SELECTION_STRING = 'count(point),' \
                                           'ST_X(ST_CENTROID(ST_COLLECT(array_agg(point)))) as point_lat,' \
                                           'ST_Y(ST_CENTROID(ST_COLLECT(array_agg(point)))) as point_lon,' \
                                 'avg(modifier_v1) as modifier_v1, avg(modifier_v2) as modifier_v2'

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


def _parse_map_candidate(
        record: Record,
        calc_rad: float = None,
        without_count: bool = True
) -> MapCandidate:
    items = dict(record.items())

    items['point'] = Georaphy(lat=items.pop('point_lat'), lon=items.pop('point_lon'))

    items['color_v1'] = get_color_grad(items['modifier_v1'])
    items['color_v2'] = get_color_grad(items['modifier_v2'])
    if calc_rad:
        items['calculated_radius'] = calc_rad
    if without_count:
        items['count'] = 1

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
        filter: CandidateFilter,
        aggregate: bool = True
) -> list[MapCandidate]:
    sql_count = f"SELECT count(point) as c FROM {Tables.candidates} " \
          f"WHERE "
    values = [to_postgis_poly(filter.to_poly())]
    ph_i = 2
    filter_string = ' '
    if filter.abbrev_ao:
        filter_string += f" abbrev_ao = ${ph_i} AND "
        ph_i += 1
        values.append(filter.abbrev_ao)

    if filter.min_modifier_v1 != 0:
        filter_string += f" modifier_v1 >= ${ph_i} AND "
        ph_i += 1
        values.append(filter.min_modifier_v1)

    if filter.min_modifier_v2 != 0:
        filter_string += f" modifier_v2 >= ${ph_i} AND "
        ph_i += 1
        values.append(filter.min_modifier_v2)

    if filter.max_modifier_v2 != 1:
        filter_string += f" modifier_v2 <= ${ph_i} AND "
        ph_i += 1
        values.append(filter.max_modifier_v2)

    if filter.max_modifier_v1 != 1:
        filter_string += f" modifier_v1 <= ${ph_i} AND "
        ph_i += 1
        values.append(filter.max_modifier_v1)

    if filter.types:
        f = lambda x: f'\'{x}\''
        filter_string += f" type IN ('any', {','.join(map(f, filter.types))}) AND "

    if filter.districts_ids:
        filter_string += f" district_id IN ({','.join(map(str, filter.districts_ids))}) AND "

    filter_string += " ST_CONTAINS($1, point) "

    count = (await pool.fetchrow(sql_count + filter_string, *values))['c']
    aggregate_radius = min(700, BASE_CALCULATED_RADIUS * max(1, (count / MAX_SCREEN_CANDIDATES)))

    if not aggregate or (aggregate_radius <= BASE_CALCULATED_RADIUS + 1):
        sql = f'SELECT {MAP_CANDIDATE_SELECTION_STRING} FROM {Tables.candidates} WHERE '
        records = await pool.fetch(sql + filter_string, *values)
        return [_parse_map_candidate(x) for x in records]
    else:
        sql = f"""SELECT {AGGREGATE_MAP_CANDIDATE_SELECTION_STRING} FROM (select
                point, modifier_v1, modifier_v2,
                ST_ClusterKMeans(
                    point,
                    {int(max(1, (count / MAX_SCREEN_CANDIDATES)))},                      
                    max_radius := {aggregate_radius}
                ) over () as cid FROM {Tables.candidates} WHERE {filter_string}) as x GROUP BY cid """
        print(sql)
        records = await pool.fetch(sql, *values)
        return [
            _parse_map_candidate(
                x, calc_rad=aggregate_radius,
                without_count=False
            ) for x in records
        ]


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


async def get_all_loaded_candidates(pool: asyncpg.Pool) -> list[(float, float, CandidateType)]:
    sql = f"SELECT ST_X(point) as point_lat, ST_Y(point) as point_lon, type FROM {Tables.candidates}"
    records = await pool.fetch(sql)

    return [(r['point_lat'], r['point_lon'], r['type']) for r in records]
