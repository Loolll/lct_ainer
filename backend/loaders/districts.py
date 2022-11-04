import asyncpg
from ast import literal_eval

from models import DistrictForm, Georaphy
from store import district as store
from misc.tools import calc_center
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)


async def load(pool: asyncpg.Pool):
    with open('/datasets/data_src/ao_areas.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                try:
                    rate, abbrev_ao, name, name_ao, _, _, _, _, cords = line.strip().split(';')
                    name = name.strip('"')

                    polygons = literal_eval(cords)

                    # todo. На текущий момент для простоты реализации учитываем лишь
                    #  самый крупный полигон района.

                    _best_i = 0
                    _best_size = 0
                    for i, poly in enumerate(polygons):
                        if _best_size < len(poly):
                            _best_size = len(poly)
                            _best_i = i

                    cords = polygons[_best_i]
                    cords.append(cords[0])  # Closing polygon rings

                    polygon = [Georaphy(lat=x[0], lon=x[1]) for x in cords]

                    center = calc_center(cords)
                    center = Georaphy(lat=center[0], lon=center[1])

                    if abbrev_ao not in ['ЗелАО', 'Новомосковский', 'Троицкий']:
                        await store.create_district(
                            pool, form=DistrictForm(
                                abbrev_ao=str(abbrev_ao),
                                name_ao=str(name_ao),
                                name=str(name).lower().replace('ё', 'е'),
                                polygon=polygon,
                                center=center,
                                reliability=rate
                            )
                        )

                        logging.info(f'LOADED {abbrev_ao} {name}')
                    else:
                        logging.info(f'SKIPPED {abbrev_ao} {name}')
                except asyncpg.UniqueViolationError:
                    # Already loaded
                    pass
