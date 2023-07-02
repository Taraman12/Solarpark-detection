# build-in
import os

DOCKERIZED = os.getenv("DOCKERIZED", "False").lower() in ("true", "1", "t")

MAKE_TRAININGS_DATA = os.getenv("MAKE_TRAININGS_DATA", "True").lower() in (
    "true",
    "1",
    "t",
)

PRODUCTION = os.getenv("PRODUCTION", "False").lower() in ("true", "1", "t")

if DOCKERIZED:
    API_HOST = os.getenv("API_HOST", "api").lower()
    ML_HOST = os.getenv("ML_HOST", "ml-serve").lower()
else:
    API_HOST = os.getenv("API_HOST", "localhost").lower()
    ML_HOST = os.getenv("ML_HOST", "localhost").lower()


# MAKE_TRAININGS_DATA = True
# PRODUCTION = False