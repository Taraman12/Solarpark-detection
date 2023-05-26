# build-in
import os

DOCKERIZED = bool(os.getenv("DOCKERIZED", False))

MAKE_TRAININGS_DATA = bool(os.getenv("MAKE_TRAININGS_DATA", True))

PRODUCTION = bool(os.getenv("PRODUCTION", False))
