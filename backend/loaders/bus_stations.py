import asyncio
import json
import asyncpg
from contextlib import suppress

from models import BusStationForm, Georaphy
from store import bus_station as store
from store.district import get_point_district
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

AVERAGE_ROUTES_COUNT = None
MAX_ROUTES_COUNT = 0


async def load(pool: asyncpg.Pool):
    global MAX_ROUTES_COUNT, AVERAGE_ROUTES_COUNT

    routes_count = 0
    routes_total = 0

    with open('/datasets/data_src/bus_stations.json', encoding='cp1251') as file:
        bus_stations = json.load(file)

    for station in bus_stations:
        routes = len(station["RouteNumbers"].split(';'))
        routes_total += routes
        routes_count += 1
        MAX_ROUTES_COUNT = max(MAX_ROUTES_COUNT, routes)

    AVERAGE_ROUTES_COUNT = routes_total / routes_count

    i = 0

    async def _load(station):
        nonlocal i

        id = station['global_id']
        point = Georaphy(
            lat=float(station["Latitude_WGS84"]),
            lon=float(station["Longitude_WGS84"])
        )
        routes = len(station["RouteNumbers"].split(';'))
        address = station['Name']

        district = await get_point_district(pool, point)

        if not district:
            i += 1
            return

        with suppress(asyncpg.UniqueViolationError):
            await store.create_bus_station(
                pool, form=BusStationForm(
                    id=id,
                    address=address,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    modifier=routes/MAX_ROUTES_COUNT,
                    point=point
                )
            )

        i += 1
        if not i % 25:
            logging.info(f"LOADED BUS STATIONS {i/routes_count:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for station in bus_stations:
        tasks.append(loop.create_task(_load(station)))

    await asyncio.wait(tasks)
