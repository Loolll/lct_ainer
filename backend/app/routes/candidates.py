from fastapi import APIRouter, Depends
from asyncpg import Pool

from misc.db import get_db
from store import candidates as store
from models import Candidate, BboxQuery, Georaphy, MapCandidate, HeatmapCandidate, ModifierType
from services import candidates

router = APIRouter(tags=['Candidates'])


@router.post(path='/bbox', response_model=list[MapCandidate])
async def get_by_bbox_candidates(
        bbox: BboxQuery,
        pool: Pool = Depends(get_db)
):
    return await store.get_bbox_map_candidates(pool, poly=bbox.to_poly())


@router.post(path='/calc', response_model=Candidate)
async def calc_new_candidate(
        point: Georaphy,
        radius: float = 400,
        pool: Pool = Depends(get_db)
):
    return await candidates.get_point_candidate(
        pool=pool,
        radius=radius,
        point=point
    )


@router.post(path='/heatmap', response_model=list[HeatmapCandidate])
async def get_candidates_heatmap(
        bbox: BboxQuery,
        pool: Pool = Depends(get_db),
        modifier_type: ModifierType = ModifierType.modifier_v1
):
    return await store.get_bbox_heatmap_candidates(
        pool=pool,
        poly=bbox.to_poly(),
        modifier_type=modifier_type
    )
