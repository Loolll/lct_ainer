import asyncpg
from ast import literal_eval

from models import StateForm, Georaphy
from store import state as store
import logging

logging.basicConfig(encoding='utf-8', level=logging.INFO)


async def load(pool: asyncpg.Pool):
    with open('/datasets/data_src/ao_self.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                try:
                    rate, abbrev, name, cords, _ = line.strip().split(';')
                    polygons = []

                    cords = literal_eval(cords)
                    for poly in cords:
                        polygon = poly + [poly[0]]  # Closing polygon rings
                        polygons.append([Georaphy(lat=x[0], lon=x[1]) for x in polygon])

                    await store.create_state(
                        pool, form=StateForm(
                            abbrev=str(abbrev),
                            name=str(name),
                            polygons=polygons,
                            # center=center,
                            reliability=rate
                        )
                    )

                    logging.info(f'LOADED {abbrev}')
                except asyncpg.UniqueViolationError:
                    # Already loader
                    pass
