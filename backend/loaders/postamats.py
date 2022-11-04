import asyncpg
from collections import defaultdict

from models import PostamatForm, Georaphy
from store import postamat as store
from store.metro import get_metro
from store.district import get_point_district
from misc.tools import calc_center
from datasets.tools import fetch_metro_name, fetch_postamat_work_hours


AVERAGE_WORK_HOURS = None
COMPANY_RATE = {}


async def load(pool: asyncpg.Pool):
    company_count = defaultdict(int)
    max_company_count = 0
    hours_count = 0
    hours_total = 0

    with open('/datasets/data_src/postamats.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                line = line.strip().replace('ё', 'е')

                _, id, city, _, _, name, _, metro, _, _, \
                _, _, work_time, _, _, _, _, lat, lon, _, *_ = line.split(';')

                if city != 'Москва':
                    continue

                company = name.split(':')[1].strip().lower()
                company_count[company] += 1

                hours_total += fetch_postamat_work_hours(work_time)
                hours_count += 1

    max_company_count = max(company_count.values())

    for key in company_count:
        COMPANY_RATE[key] = company_count[key] / max_company_count

    with open('/datasets/data_src/postamats.csv') as file:
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                try:
                    line = line.strip().replace('ё', 'е')

                    _, id, city, _, _, name, address, metro, _, _, \
                    _, _, work_time, _, _, _, _, lat, lon, _, *_ = line.split(';')

                    if city != 'Москва':
                        continue

                    company = name.split(':')[1].strip().lower()

                    if metro.strip():
                        metro = await get_metro(pool, station=fetch_metro_name(metro), return_none=True)
                    else:
                        metro = None

                    point = Georaphy(lat=lat, lon=lon)

                    hours = fetch_postamat_work_hours(work_time)

                    if metro:
                        district_id = metro.district_id
                        abbrev_ao = metro.abbrev_ao
                    else:
                        district = await get_point_district(pool, point)
                        if not district:
                            continue
                        district_id = district.id
                        abbrev_ao = district.abbrev_ao

                    await store.create_postamat(
                        pool, form=PostamatForm(
                            id=id,
                            address=address,
                            point=point,
                            company=company,
                            abbrev_ao=abbrev_ao,
                            district_id=district_id,
                            metro_id=metro.id if metro else None,
                            hours_modifier=hours / 24,
                            company_modifier=COMPANY_RATE[company],
                            result_modifier=(hours / 24) * COMPANY_RATE[company]
                        )
                    )

                    print(f'LOADED {id}')
                except asyncpg.UniqueViolationError:
                    # Already loader
                    pass
