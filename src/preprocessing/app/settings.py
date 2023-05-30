# build-in
import os

DOCKERIZED = os.getenv("DOCKERIZED", "False").lower() in ("true", "1", "t")

MAKE_TRAININGS_DATA = os.getenv("MAKE_TRAININGS_DATA", "True").lower() in (
    "true",
    "1",
    "t",
)

PRODUCTION = os.getenv("PRODUCTION", "False").lower() in ("true", "1", "t")
