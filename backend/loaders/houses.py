import asyncio
import json
import asyncpg
from contextlib import suppress
from pydantic import BaseModel
from typing import Optional, Any

import logging
from tensorflow.python import keras
from tensorflow.python.keras import optimizers
from tensorflow.python.keras import layers

from pullenti.address.AddressService import AddressService

from models import Georaphy, HouseForm
from store import houses as store
from store.district import get_point_district
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

logging.basicConfig(encoding='utf-8', level=logging.INFO)

# AVERAGE_CAPACITY = None
MAX_SQUARE = 0
MAX_YEAR = 0
MAX_FLOORS = 0
MAX_ENTRANCES = 0
MAX_ROOMS = 0
AVERAGE_SQUARE = 0
AVERAGE_YEAR = 0
AVERAGE_FLOORS = 0
AVERAGE_ENTRANCES = 0
AVERAGE_ROOMS = 0

models = {}
datasets = {}


logging.info("Initializing TensorFlow models")

for square in [True, False, None]:
    for year in [True, False, None]:
        for floors in [True, False, None]:
            for entrances in [True, False, None]:
                for rooms in [True, False, None]:
                    all = [square, year, floors, entrances, rooms]

                    if len([x for x in all if x is None]) != 1:
                        continue

                    if len([x for x in all if not bool(x)]) > 3:
                        continue

                    model = keras.Sequential()
                    model.add(layers.Flatten(input_shape=(len([x for x in all if bool(x)]), )))
                    model.add(layers.Dense(3, activation='linear'))
                    model.add(layers.Dense(2, activation='softmax'))
                    model.add(layers.Dense(1, activation='linear'))
                    model.compile(
                        loss='mean_squared_error',
                        optimizer=optimizers.adam_v2.Adam(0.005)
                    )

                    models[(square, year, floors, entrances, rooms)] = model
                    datasets[(square, year, floors, entrances, rooms)] = ([], [])

logging.info('OK')

logging.info(f"Initializing pullenti")
AddressService.initialize()
AddressService.set_gar_index_path("/datasets/data_src/Gar77")
AddressService.set_default_geo_object("Москва")
logging.info(f'OK {AddressService.get_gar_statistic()}')
# logging.info(str(
#     AddressService.process_single_address_text(
#         'проезд. нагатинский 1-й, д. 11, к. 3, москва'.lower()
#     ).items[-1].gars[0].get_params()
# ))
# logging.info(str(
#     AddressService.process_single_address_text(
#         'г Москва, пр-кт Мира, д 188Б к 1'.lower()
#     ).items[-1].gars[0].get_params()
# ))
# logging.info(str(
#     AddressService.process_single_address_text(
#         'пр-кт мира, д 188 б, к 1, москва'.lower()
#     ).items[-1].gars[0].get_params()
# ))
# logging.info(str(
#     AddressService.process_single_address_text(
#         'г Москва, пр-кт Мира, д 188Б к 1'.lower()
#     ).items[-1].gars[0].get_params()
# ))


def get_normalize_value(key: str) -> float:
    _map = {
        'square': MAX_SQUARE,
        'year': MAX_YEAR,
        'floors': MAX_FLOORS,
        'entrances': MAX_ENTRANCES,
        'rooms': MAX_ROOMS
    }
    return _map[key]


def get_average_value(key: str) -> float:
    _map = {
        'square': AVERAGE_SQUARE,
        'year': AVERAGE_YEAR,
        'floors': AVERAGE_FLOORS,
        'entrances': AVERAGE_ENTRANCES,
        'rooms': AVERAGE_ROOMS
    }
    return _map[key]


def normalize_address(address: str) -> str:
    return address.lower().replace('.', '').replace(' к ', ' корп ')


def fetch_identif(address: str) -> str:
    address = normalize_address(address)
    processed = AddressService.process_single_address_text(address)

    for i in range(7, 4, -1):
        with suppress(Exception):
            return processed.items[-1].gars[0].get_param_value(i)
        raise

identif_to_cord = {}


class RegistryInfo(BaseModel):
    id: Optional[str]
    address: Optional[Any]
    point: Optional[Georaphy]

    square: Optional[float]
    year: Optional[int]
    floors: Optional[int]
    entrances: Optional[int]
    rooms: Optional[float]

    @staticmethod
    def get_name_by_index(i: int):
        if i == 0:
            return 'square'
        elif i == 1:
            return 'year'
        elif i == 2:
            return 'floors'
        elif i == 3:
            return 'entrances'
        elif i == 4:
            return 'rooms'

    def to_bitmap(self, calc: str = None) -> tuple[
        bool | None, bool | None, bool | None, bool | None, bool | None
    ]:
        return (
            self.square is not None if calc != 'square' else None,
            self.year is not None if calc != 'year' else None,
            self.floors is not None if calc != 'floors' else None,
            self.entrances is not None if calc != 'entrances' else None,
            self.rooms is not None if calc != 'rooms' else None,
        )

    def to_inputs(self, *_except) -> tuple:
        return tuple(
            [
                x for x in [
                    self.square if 'square' not in _except else None,
                    self.year if 'year' not in _except else None,
                    self.floors if 'floors' not in _except else None,
                    self.entrances if 'entrances' not in _except else None,
                    self.rooms if 'rooms' not in _except else None,
                ] if x is not None
            ]
        )

    def apply_to_train_datasets(self) -> None:
        values = {
            'square': self.square / MAX_SQUARE if self.square else None,
            'year': self.year / MAX_YEAR if self.year else None,
            'floors': self.floors / MAX_FLOORS if self.floors else None,
            'entrances': self.entrances / MAX_ENTRANCES if self.entrances else None,
            'rooms': self.rooms / MAX_ROOMS if self.rooms else None
        }
        _except = [None, *list(values.keys())]

        if sum([int(x) for x in self.to_bitmap()]) == 5:
            for name, value in values.items():
                for _except_1 in _except:
                    for _except_2 in _except:
                        if _except_1 == _except_2:
                            continue

                        train = RegistryInfo(
                            address=self.address,
                            **{k: v for k, v in values.items() if k not in [name, _except_1, _except_2]}
                        )
                        inputs = train.to_inputs()
                        output = value

                        datasets[train.to_bitmap(name)][0].append(inputs)
                        datasets[train.to_bitmap(name)][1].append(output)
        elif sum([int(x) for x in self.to_bitmap()]) == 4:
            for name, value in values.items():
                for _except_1 in _except:
                    if value is None:
                        continue

                    train = RegistryInfo(
                        address=self.address,
                        **{k: v for k, v in values.items() if k not in [name, _except_1]}
                    )
                    inputs = train.to_inputs()
                    output = value

                    datasets[train.to_bitmap(name)][0].append(inputs)
                    datasets[train.to_bitmap(name)][1].append(output)
        elif sum([int(x) for x in self.to_bitmap()]) == 3:
            for name, value in values.items():
                if value is None:
                    continue

                train = RegistryInfo(
                    address=self.address,
                    **{k: v for k, v in values.items() if k not in [name]}
                )
                inputs = train.to_inputs()
                output = value

                datasets[train.to_bitmap(name)][0].append(inputs)
                datasets[train.to_bitmap(name)][1].append(output)

    def set_by_index(self, i: int, value):
        if i == 0:
            self.square = value
        elif i == 1:
            self.year = value
        elif i == 2:
            self.floors = value
        elif i == 3:
            self.entrances = value
        elif i == 4:
            self.rooms = value
        else:
            raise RuntimeError

    def get_by_index(self, i: int):
        if i == 0:
            return self.square
        elif i == 1:
            return self.year
        elif i == 2:
            return self.floors
        elif i == 3:
            return self.entrances
        elif i == 4:
            return self.rooms
        else:
            raise RuntimeError

    def extrapolate_additional_data(self):
        bitmap = self.to_bitmap()

        match len([x for x in bitmap if bool(x)]):
            case 0 | 1 | 2:
                for i, exist in enumerate(bitmap):
                    if not exist:
                        self.set_by_index(i, get_average_value(self.get_name_by_index(i)) / 1.25)
                return
            case 5:
                return
            case _:
                predict = {
                    'square': self.square / MAX_SQUARE if self.square else None,
                    'year': self.year / MAX_YEAR if self.year else None,
                    'floors': self.floors / MAX_FLOORS if self.floors else None,
                    'entrances': self.entrances / MAX_ENTRANCES if self.entrances else None,
                    'rooms': self.rooms / MAX_ROOMS if self.rooms else None
                }

                new = RegistryInfo(**self.dict())

                for i, exist in enumerate(bitmap):
                    if not exist:
                        route: tuple = tuple([*bitmap[:i], None, *bitmap[i+1:]])
                        predict_model = RegistryInfo(
                            **predict,
                            address=self.address,
                            point=self.point
                        )
                        inputs = predict_model.to_inputs()

                        prediction = models[route].predict([inputs])[0][0]
                        response = prediction * get_normalize_value(self.get_name_by_index(i))

                        new.set_by_index(i, response)

                for i, exist in enumerate(bitmap):
                    self.set_by_index(i, new.get_by_index(i))

    def approximate_persons(self) -> float:
        return self.rooms * 3.3798


def _normalize_input(x: str) -> Optional[str]:
    x = x.strip().lower().replace('ё', 'е')

    if not len(x):
        return None
    elif x == 'не заполнено':
        return None
    elif x == 'не указано':
        return None

    return x


def parse_dadata_dumps():
    count = len(os.listdir('/datasets/data_src/dadata'))
    ready = set()

    load_identificators()

    for value in identif_to_cord.values():
        ready.add(value['address'])

    for i, path in enumerate(os.listdir('/datasets/data_src/dadata')):
        with open(f'/datasets/data_src/dadata/{path}', 'r') as file:
            for line in file:
                with suppress(Exception):
                    line = line.strip().strip(',').strip()
                    data = json.loads(line)

                    for house in data:
                        with suppress(Exception):
                            address = house['value']

                            if address in ready:
                                continue

                            identif = fetch_identif(address)

                            point = Georaphy(
                                lat=house['data']['geo_lat'],
                                lon=house['data']['geo_lon']
                            )

                            identif_to_cord[identif] = {'point': point.to_json(), 'address': address}

                            ready.add(address)

        with open(f'/datasets/data_src/identif_houses.json', 'w') as file:
            json.dump(identif_to_cord, file, ensure_ascii=False)

        logging.info(f"LOADED IDENTIFICATORS {path} {i / count:.2%}")


def load_identificators():
    global identif_to_cord

    with open(f'/datasets/data_src/identif_houses.json') as file:
        identif_to_cord = json.load(file)


async def load(pool: asyncpg.Pool):
    global MAX_SQUARE, MAX_ENTRANCES, MAX_ROOMS, MAX_YEAR, MAX_FLOORS
    global AVERAGE_SQUARE, AVERAGE_ENTRANCES, AVERAGE_ROOMS, AVERAGE_YEAR, AVERAGE_FLOORS

    # Already done
    # parse_dadata_dumps()

    load_identificators()

    counter = {
        'square': [0, 0, 0],
        'year': [0, 0, 0],
        'entrances': [0, 0, 0],
        'floors': [0, 0, 0],
        'rooms': [0, 0, 0]
    }
    registry_obj = []

    with open('/datasets/data_src/houses_registry.csv') as file:
        lines = len(list(file))

    wrong_address_metrics = []

    with open('/datasets/data_src/houses_registry.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue

            line = line.strip()

            _, _, address, square, year, floors, entrances, rooms = map(
                _normalize_input,
                line.split(';')
            )

            if year and int(year) < 1800:
                continue
            elif floors and int(floors) < 1:
                continue
            elif square:
                square = square.replace(',', '.')
                try:
                    square = float(square)
                    if square < 1:
                        continue
                except:
                    continue

            try:
                try:
                    identif = fetch_identif(address)
                    point = Georaphy.from_json(identif_to_cord[identif]['point'])
                except:
                    wrong_address_metrics.append(address)
                    raise

                info = RegistryInfo(
                    id=identif,
                    address=address,
                    point=point,
                    square=square,
                    year=year,
                    floors=floors,
                    entrances=entrances,
                    rooms=rooms
                )

                if square:
                    counter['square'][0] += info.square
                    counter['square'][1] += 1
                    counter['square'][2] = max(counter['square'][2], info.square)
                if year:
                    counter['year'][0] += info.year
                    counter['year'][1] += 1
                    counter['year'][2] = max(counter['year'][2], info.year)
                if floors:
                    counter['floors'][0] += info.floors
                    counter['floors'][1] += 1
                    counter['floors'][2] = max(counter['floors'][2], info.floors)
                if entrances:
                    counter['entrances'][0] += info.entrances
                    counter['entrances'][1] += 1
                    counter['entrances'][2] = max(counter['entrances'][2], info.entrances)
                if rooms:
                    counter['rooms'][0] += info.rooms
                    counter['rooms'][1] += 1
                    counter['rooms'][2] = max(counter['rooms'][2], info.rooms)

                registry_obj.append(info)
            except Exception as exc:
                if 'validation error for registryinfo' in str(exc).lower():
                    continue

            if not i % 25 or lines - i < 25:
                logging.info(f"LOADING HOUSES & ADDRESSES FROM FILE {i/lines:.2%}")

    # logging.info(f"WRONG ADDRESSES {wrong_address_metrics}")
    logging.info(f"WRONG ADDRESSES {len(wrong_address_metrics)}")

    AVERAGE_SQUARE = counter['square'][0] / counter['square'][1]
    AVERAGE_YEAR = counter['year'][0] / counter['year'][1]
    AVERAGE_ENTRANCES = counter['entrances'][0] / counter['entrances'][1]
    AVERAGE_FLOORS = counter['floors'][0] / counter['floors'][1]
    AVERAGE_ROOMS = counter['rooms'][0] / counter['rooms'][1]
    MAX_SQUARE = counter['square'][2]
    MAX_YEAR = counter['year'][2]
    MAX_ENTRANCES = counter['entrances'][2]
    MAX_FLOORS = counter['floors'][2]
    MAX_ROOMS = counter['rooms'][2]

    for x in registry_obj:
        x.apply_to_train_datasets()

    _count = len(datasets.keys())
    for i, key in enumerate(datasets.keys()):
        logging.info(f"TRAINING EXTRAPOLATION MODELS {i / _count:.2%}")

        if not len(datasets[key][0]):
            continue

        models[key].fit(
            x=datasets[key][0],
            y=datasets[key][1],
            epochs=20,
            verbose=False,
            use_multiprocessing=True,
            workers=16
        )

    MAX_PERSONS = 0

    rows = len(registry_obj)
    i = 0

    for i, x in enumerate(registry_obj):
        x.extrapolate_additional_data()
        MAX_PERSONS = max(MAX_PERSONS, x.approximate_persons())
        if not i % 25 or i+1 == rows:
            logging.info(f"EXTRAPOLATE DATA {i/rows:.2%}")

    with open('/datasets/extrapolated_houses.json', 'w') as file:
        data = [x.dict() for x in registry_obj]
        json.dump(data, file, ensure_ascii=False)

    i = 0

    async def _load(obj: RegistryInfo):
        nonlocal i

        district = await get_point_district(pool, obj.point)

        if not district:
            i += 1
            return

        with suppress(asyncpg.UniqueViolationError):
            await store.create_house(
                pool, form=HouseForm(
                    id=obj.id,
                    address=obj.address,
                    point=obj.point,
                    abbrev_ao=district.abbrev_ao,
                    district_id=district.id,
                    modifier=obj.approximate_persons() / MAX_PERSONS
                )
            )

        i += 1
        if not i % 25 or i == rows:
            logging.info(f"LOADED HOUSES {i / rows:.2%}")

    tasks = []
    loop = asyncio.get_event_loop()

    for x in registry_obj:
        tasks.append(loop.create_task(_load(x)))

    await asyncio.wait(tasks)
