from fastapi import APIRouter, Depends
from asyncpg import Pool

from misc.db import get_db
from store import state as store
from models import State


router = APIRouter(tags=['States'])


@router.get(path='/all', response_model=list[State])
async def get_all_states(pool: Pool = Depends(get_db)):
    return await store.get_all_states(pool)
