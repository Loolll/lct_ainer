from uuid import uuid4

from fastapi import APIRouter, Depends
from asyncpg import Pool
import csv

from misc.db import get_db
from store import candidates as store
from models import CandidateFilter,\
    Georaphy, MapCandidate
from services import candidates

router = APIRouter(tags=['Candidates'])


@router.post(path='/filter', response_model=list[MapCandidate])
async def get_candidates_by_filter(
        query: CandidateFilter,
        pool: Pool = Depends(get_db)
):
    return await store.get_bbox_map_candidates(pool, filter=query)


@router.post(path='/calc', response_model=MapCandidate)
async def calc_new_candidate(
        point: Georaphy,
        radius: float = 400,
        pool: Pool = Depends(get_db)
):
    candidate = await candidates.get_point_candidate(
        pool=pool,
        radius=radius,
        point=point
    )
    return MapCandidate.from_full(candidate)


@router.post(path='/export')
async def export_candidates(
        query: CandidateFilter,
        pool: Pool = Depends(get_db),
):
    candidates = await store.get_bbox_map_candidates(pool, filter=query)

    name = f'{uuid4()}.csv'
    path = f'/share/static/{name}'
    link = f'/static/{name}'

    with open(path, 'w') as file:
        keys = ['№', 'point_lat', 'point_lon'] + [
            k for k in candidates[0].dict().keys()
            if k not in ['point', ]
        ]

        writer = csv.DictWriter(file, keys)
        writer.writeheader()
        for i, x in enumerate(candidates, 1):
            obj = x.dict()
            obj['№'] = i
            point = obj.pop('point')
            obj['point_lat'], obj['point_lon'] = point['lat'], point['lon']
            writer.writerow(obj)

    return {'link': link}
