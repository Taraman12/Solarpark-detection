from typing import Dict
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.core.config import settings
from app.models.solarpark import SolarPark
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate
from app.tests.utils.utils import random_lower_string


def create_random_solarpark(db: Session) -> SolarPark:
    name_of_model = random_lower_string()
    size_in_sq_m = 100.0
    peak_power = 100.0
    date_of_data = date(2021, 1, 1)
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [1.0, 2.0]
    lon = [1.0, 2.0]
    solarpark_in = SolarParkCreate(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        date_of_data=date_of_data,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
    )
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    return solarpark
