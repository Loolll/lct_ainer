from fastapi import APIRouter, Depends
from asyncpg import Pool

from misc.db import get_db
from store import state as store
from models import State, BboxQuery, StateAutocompleteResponse


router = APIRouter(tags=['States'])


@router.get(path='/all', response_model=list[State])
async def get_all_states(pool: Pool = Depends(get_db)):
    return await store.get_all_states(pool)


@router.post(path='/bbox', response_model=list[State])
async def get_by_bbox_states(
        bbox: BboxQuery,
        pool: Pool = Depends(get_db)
):
    return await store.get_bbox_states(pool, poly=bbox.to_poly())


@router.get(path='/autocomplete', response_model=StateAutocompleteResponse)
async def autocomplete_states(query: str = '', pool: Pool = Depends(get_db)):
    return await store.autocomplete_states(pool, query=query)


@router.get(path='/', response_model=State)
async def get_state(abbrev: str, pool: Pool = Depends(get_db)):
    return await store.get_state(pool, abbrev=abbrev)

