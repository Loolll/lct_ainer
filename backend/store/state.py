import asyncpg
from asyncpg import Record

from misc.db import Tables
from models import StateForm, State, from_postgis_polygons, to_postgis_polygons, to_postgis_point, Georaphy
from exceptions import StateNotFoundedError


SELECTION_STRING = 'abbrev, name, ST_AsText(polygons) as polygons, reliability'

def _parse_state(
        record: Record,
        return_none: bool = False
) -> State | None:
    if record:
        items = dict(record.items())

        items['polygons'] = from_postgis_polygons(items['polygons'])
        # items['center'] = Georaphy(lat=items.pop('center_lat'), lon=items.pop('center_lon'))

        return State.parse_obj(items)
    else:
        if return_none:
            return None
        else:
            raise StateNotFoundedError


async def get_state(
        pool: asyncpg.Pool,
        abbrev: str,
        return_none: bool = False
) -> State:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.states} WHERE abbrev = $1"
    record = await pool.fetchrow(sql, abbrev)

    return _parse_state(record, return_none)


async def create_state(
        pool: asyncpg.Pool,
        form: StateForm,
) -> State:
    sql = f"INSERT INTO {Tables.states} (abbrev, name, polygons, reliability) " \
          f"VALUES ($1, $2, $3, $4) RETURNING {SELECTION_STRING}"
    record = await pool.fetchrow(
        sql, form.abbrev, form.name,
        to_postgis_polygons(form.polygons),
        # to_postgis_point(form.center),
        form.reliability
    )
    return _parse_state(record, False)


async def get_all_states(pool: asyncpg.Pool) -> list[State]:
    sql = f"SELECT {SELECTION_STRING} FROM {Tables.states}"
    return [_parse_state(x) for x in await pool.fetch(sql)]
