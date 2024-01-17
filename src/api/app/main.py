# third party
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

# local modules
from app.api_core.api_v1.api import api_router
from app.api_core.errors.http_error import http_error_handler
from app.api_core.errors.validation_error import http422_error_handler
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

# TODO: Update description and tags_metadata

description = """
This is the API for the Solarpark Detection Project: [Github Solarpark-detection](https://github.com/Taraman12/Solarpark-detection).

## Solarpark
In this project a solarpark is defined as a polygon with a name and a unique ID.\n
The solarpark is used to group the prediction from every date.\n
Each prediction is assigned to a solarpark (see prediction).

## Prediction
An prediction is a polygon with a date, size, confidence etc.\n
It is the result of the ml-model used to detect solarparks from sentinel-2 imagery.\n
The prediction is assigned to a solarpark (n:1) to be validated.\n

"""

tags_metadata = [
    {
        "name": "root",
        "description": "Check if the API is running.",
    },
    {
        "name": "solarpark",
        "description": "The solarpark is used to group the predictions from different dates.",
    },
    {
        "name": "prediction",
        "description": "Predictions are made from a self trained U-Net.",
    },
    {
        "name": "service",
        "description": "Operations with the microservices and docker.",
    },
    {
        "name": "instance",
        "description": "Operations to keep track of the ec2 instances.",
    },
    {
        "name": "models",
        "description": "Operations to CRUD models to and from the ml server.",
    },
    {
        "name": "login",
        "description": "Login to the API.",
    },
    {
        "name": "user",
        "description": "A user needs to be registered to use the API post/put/delete methods.",
    },
]


def get_application() -> FastAPI:
    application = FastAPI(
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
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],  # Content-Type
            expose_headers=["*"],
        )
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = get_application()


# will be moved to a startup script
# @app.on_event("startup")
# async def startup_event():
db = SessionLocal()
init_db(db)
