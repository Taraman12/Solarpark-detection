# third-party
from fastapi import APIRouter

# local modules
from .endpoints import instance, root, solarpark, models

api_router = APIRouter()

api_router.include_router(root.router, tags=["root"])
api_router.include_router(solarpark.router, prefix="/solarpark", tags=["solarpark"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(instance.router, prefix="/instance", tags=["instance"])
