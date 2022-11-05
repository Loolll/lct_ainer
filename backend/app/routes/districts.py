from fastapi import APIRouter, Depends
from asyncpg import Pool

from misc.db import get_db
from store import district as store
from models import District, DistrictFilter, DistrictAutocompleteResponse


router = APIRouter(tags=['Districts'])


@router.get(path='/all', response_model=list[District])
async def get_all_districts(pool: Pool = Depends(get_db)):
    return await store.get_all_districts(pool)


@router.get(path='/search', response_model=list[District])
async def search_districts(ao_abbrev: str, pool: Pool = Depends(get_db)):
    return await store.get_state_districts(pool, ao_abbrev)


@router.get(path='/autocomplete', response_model=DistrictAutocompleteResponse)
async def autocomplete_districts(query: str = '', pool: Pool = Depends(get_db)):
    return await store.autocomplete_districts(pool, query=query)


@router.get(path='/', response_model=District)
async def get_district(id: int, pool: Pool = Depends(get_db)):
    return await store.get_district(pool, id=id)


@router.post(path='/bbox', response_model=list[District])
async def get_by_bbox_districts(
        query: DistrictFilter,
        pool: Pool = Depends(get_db)
):
    return await store.get_bbox_districts(pool, filter=query)
