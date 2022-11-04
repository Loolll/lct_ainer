from fastapi import APIRouter, Depends
from asyncpg import Pool

from misc.db import get_db
from store import district as store
from models import District, BboxQuery


router = APIRouter(tags=['Districts'])


@router.get(path='/all', response_model=list[District])
async def get_all_districts(pool: Pool = Depends(get_db)):
    return await store.get_all_districts(pool)


@router.get(path='/search', response_model=list[District])
async def search_districts(ao_abbrev: str, pool: Pool = Depends(get_db)):
    return await store.get_state_districts(pool, ao_abbrev)


@router.post(path='/bbox', response_model=list[District])
async def get_by_bbox_districts(
        bbox: BboxQuery,
        pool: Pool = Depends(get_db)
):
    return await store.get_bbox_districts(pool, poly=bbox.to_poly())

