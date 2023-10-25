# third party
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# local modules
from app.api_core.api_v1.api import api_router
from app.core.config import settings

# os.chdir(Path(__file__).parent)
description = """
This is the API for the Solarpark Detection Project.

## Solarpark
in this project a solarpark is defined as a polygon with a name and a unique ID.
The solarpark is used to group the observations.
Each observation is assigned to a solarpark.

## Observation
An observation is a polygon with a date, a name, a confidence and a size.
The observation is used to detect the solarpark.
The observation is assigned to a solarpark.

"""

tags_metadata = [
    {
        "name": "root",
        "description": "Check if the API is running.",
    },
    {
        "name": "solarpark",
        "description": "Operations with solarparks. The solarpark is used to group the observations.",
    },
    {
        "name": "solarpark_observation",
        "description": "Operations with solarpark observations. The observation is used to detect the solarpark.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description=description,
    docs_url="/docs",
    redoc_url=None,
    openapi_tags=tags_metadata,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
