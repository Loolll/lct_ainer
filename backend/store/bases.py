import asyncpg
from typing import Callable
from models import Nearest, Georaphy


def parse_nearest(record: asyncpg.Record, func: Callable) -> Nearest:
    items = dict(record)
    distance = items.pop('distance')

    obj = func(record)

    return Nearest(obj=obj, distance=distance)


async def get_nearest(
        pool: asyncpg.Pool,
        point: Georaphy,
        max_radius: float,
        selection_string: str,
        table: str,
        parse_func: Callable,
        point_row_name: str = 'point',
) -> list[Nearest]:
    sql = f"SELECT {selection_string}, " \
          f"ST_DISTANCE({point_row_name}::geography, ST_POINT($1, $2, 4326)::geography) as distance " \
          f"FROM {table} " \
          f"WHERE " \
          f"ST_DISTANCE({point_row_name}::geography, ST_POINT($1, $2, 4326)::geography) <= $3 " \
          f"ORDER BY ST_DISTANCE({point_row_name}::geography, ST_POINT($1, $2, 4326)::geography) ASC "

    records = await pool.fetch(sql, point.lat, point.lon, max_radius)

    return [parse_nearest(x, parse_func) for x in records]
