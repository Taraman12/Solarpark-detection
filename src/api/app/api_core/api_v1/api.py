# third-party
from fastapi import APIRouter

# local modules
from .endpoints import (
    instance,
    login,
    models,
    root,
    solarpark,
    solarpark_observation,
    user,
)

api_router = APIRouter()

api_router.include_router(root.router, tags=["root"])
api_router.include_router(solarpark.router, prefix="/solarpark", tags=["solarpark"])
api_router.include_router(
    solarpark_observation.router,
    prefix="/solarpark_observation",
    tags=["solarpark_observation"],
)
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(instance.router, prefix="/instance", tags=["instance"])
