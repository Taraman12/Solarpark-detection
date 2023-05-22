# third-party
from fastapi import APIRouter

# local modules
from .endpoints import solarpark, root

api_router = APIRouter()

api_router.include_router(root.router, tags=["root"])
api_router.include_router(
    solarpark.router, prefix="/solarpark", tags=["solarpark"]
)

