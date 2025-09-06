from fastapi import APIRouter

from api.routes import indexer
# from api.routes import predictor

router = APIRouter()
router.include_router(indexer.router, tags=["indexer"], prefix="/v1")
