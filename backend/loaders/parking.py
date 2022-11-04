import json
import asyncpg
from contextlib import suppress

from models import ParkingForm, Georaphy
from store import parking as store
from store.district import get_point_district
from misc.tools import calc_center
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)

AVERAGE_CAPACITY = None
MAX_CAPACITY = 0


async def load(pool: asyncpg.Pool):
    global AVERAGE_CAPACITY, MAX_CAPACITY

    capacity_count = 0
    capacity_total = 0

    with open('/datasets/data_src/parking_under.json') as file:
        parking_under = json.load(file)

    with open('/datasets/data_src/parking_street.json') as file:
        parking_street = json.load(file)

    with open('/datasets/data_src/parking_redirect.json') as file:
        parking_redirect = json.load(file)

    for dataset in [parking_under, parking_street, parking_redirect]:
        for parking in dataset['features']:
            attrs = parking['properties']['Attributes']
            capacity = attrs.get('CountSpaces', None) or attrs.get('CarCapacity')

            capacity_total += capacity
            MAX_CAPACITY = max(MAX_CAPACITY, capacity)
            capacity_count += 1

    AVERAGE_CAPACITY = capacity_total / capacity_count

    i = 0

    for dataset in [parking_under, parking_street, parking_redirect]:
        for parking in dataset['features']:
            props = parking['properties']
            attrs = props['Attributes']

            capacity = attrs.get('CountSpaces', None) or attrs.get('CarCapacity')
            id = attrs['global_id']

            address = attrs.get('Address', None) or attrs.get('ParkingName')
            cords = parking['geometry']['coordinates']
            if type(cords[0]) is float:
                point = Georaphy(lat=cords[1], lon=cords[0])
            elif type(cords[0]) is list:
                point = calc_center(cords[0])
                point = Georaphy(lat=point[1], lon=point[0])
            else:
                raise RuntimeError()

            district = await get_point_district(pool, point)

            if not district:
                continue

            with suppress(asyncpg.UniqueViolationError):
                await store.create_parking(
                    pool, form=ParkingForm(
                        id=id,
                        address=address,
                        abbrev_ao=district.abbrev_ao,
                        district_id=district.id,
                        size_modifier=capacity/MAX_CAPACITY,
                        point=point
                    )
                )

            i += 1
            if not i % 25:
                logging.info(f"LOADED PARKING {i/capacity_count:.2%}")
