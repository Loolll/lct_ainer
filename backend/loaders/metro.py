import asyncpg
from collections import defaultdict
from string import digits

from models import MetroForm, District, Georaphy
from store import metro as store
from store.district import get_district
from datasets.tools import fetch_district_name

rus_uppercase = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

async def load(pool: asyncpg.Pool):
    _stations_traffic = defaultdict(lambda *_: {'sum': 0, 'count': 0})

    with open('/datasets/data_src/metro_traffic.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                station, _, _, _, income, outcome, _ = line.strip().split(';')
                income, outcome = int(income), int(outcome)

                if (income + outcome) != 0:
                    key = station.strip().lower().replace('ё', 'е')
                    _stations_traffic[key]['sum'] += (income + outcome) / 2
                    _stations_traffic[key]['count'] += 1
                    _stations_traffic[key]['average'] = _stations_traffic[key]['sum'] / _stations_traffic[key]['count']

    _max_averages = max([_stations_traffic[k]['average'] for k in _stations_traffic])

    for k in _stations_traffic:
        _stations_traffic[k]['modifier'] = _stations_traffic[k]['average'] / _max_averages

    _average_modifier = (
            sum([_stations_traffic[k]['modifier'] for k in _stations_traffic]) /
            len(_stations_traffic.keys())
    )

    with open('/datasets/data_src/metro_entrances.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                try:
                    line = line.strip().replace('ё', 'е')

                    _, _name, _, name_ao, name_district, lon, lat, *_, status, _ = line.strip().split(';')
                    station, entrance = _name.split(',', maxsplit=1)

                    if 'закр' in status or not name_district:
                        continue

                    entrance = ''.join([x for x in entrance if x in digits])
                    entrance = int(entrance) if len(entrance) else 1

                    station = station.strip().lower()
                    abbrev_ao = ''.join([x for x in name_ao if x in rus_uppercase]) + 'АО'

                    if abbrev_ao.lower() == 'нао':
                        continue

                    district: District = await get_district(pool, name=fetch_district_name(name_district))
                    point = Georaphy(lat=lat, lon=lon)

                    await store.create_metro(
                        pool, form=MetroForm(
                            station=station,
                            entrance=entrance,
                            district_id=district.id,
                            abbrev_ao=abbrev_ao,
                            point=point,
                            traffic_modifier=_stations_traffic[station].get('modifier', _average_modifier)
                        )
                    )

                    print(f'LOADED {abbrev_ao} {district.name}: {station} {entrance}')
                except asyncpg.UniqueViolationError:
                    # Already loaded
                    pass
