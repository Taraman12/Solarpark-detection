# build-in
import os

from dotenv import load_dotenv

DOCKERIZED = os.getenv("DOCKERIZED", "False").lower() in ("true", "1", "t")

MAKE_TRAININGS_DATA = os.getenv("MAKE_TRAININGS_DATA", "True").lower() in (
    "true",
    "1",
    "t",
)

PRODUCTION = os.getenv("PRODUCTION", "False").lower() in ("true", "1", "t")

if DOCKERIZED:
    # load_dotenv()
    API_HOST = os.getenv("API_HOST", "api").lower()
    ML_HOST = os.getenv("ML_HOST", "ml-serve").lower()
    FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER", "John@doe.com")
    FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "password")
else:
    load_dotenv()
    API_HOST = os.getenv("API_HOST", "localhost").lower()
    ML_HOST = os.getenv("ML_HOST", "localhost").lower()
    FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER", "John@doe.com")
    FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD", "password")


MAKE_TRAININGS_DATA = False
PRODUCTION = True
