from fastapi import APIRouter
from .states import router as states
from .districts import router as districts
from .candidates import router as candidates


router = APIRouter(prefix='/api')
router.include_router(states, prefix='/states')
router.include_router(districts, prefix='/districts')
router.include_router(candidates, prefix='/candidates')
