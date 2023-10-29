from datetime import date

# from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud

# from app.core.config import settings
from app.models.solarpark import SolarPark

# from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate
from app.tests.utils.utils import random_lower_string


def random_solarpark() -> SolarPark:
    # NOTE geom shouldn't have a trailing zero, else the test will fail due to the change to the string
    name_of_model = [random_lower_string()]
    size_in_sq_m = 100.0
    peak_power = 100.0
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence_over_all_observations = 0.8
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [599968.55, 599970.91, 599973.65, 599971.31, 599968.55]
    lon = [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63]
    geom = "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))"
    solarpark = SolarPark(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence_over_all_observations=avg_confidence_over_all_observations,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
        geom=geom,
    )
    return solarpark


def create_random_solarpark(db: Session) -> SolarPark:
    solarpark_in = random_solarpark()
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    return solarpark
