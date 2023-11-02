# third party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# local modules
from app.api_core.api_v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

# TODO: Update description and tags_metadata

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
        "description": "The solarpark is used to group the observations.",
    },
    {
        "name": "solarpark_observation",
        "description": "Operations with solarpark observations. The observation is used to detect the solarpark.",
    },
    {
        "name": "user",
        "description": "A user needs to be registered to use the API post/put/delete methods.",
    },
    {
        "name": "login",
        "description": "Login to the API.",
    },
    {
        "name": "models",
        "description": "Operations to CRUD models to and from the ml server.",
    },
    {
        "name": "instance",
        "description": "Operations to keep track of the ec2 instances.",
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",  # {settings.API_V1_STR}
    description=description,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=None,
    openapi_tags=tags_metadata,
    # root_path="/api/v1",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],  # Content-Type
        expose_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# will be moved to a startup script
db = SessionLocal()
init_db(db)
