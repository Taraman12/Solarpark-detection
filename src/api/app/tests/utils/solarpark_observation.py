from datetime import date

from sqlalchemy.orm import Session

from app import crud

# from app.core.config import settings
from app.models.solarpark_observation import SolarParkObservation
from app.tests.utils.utils import random_lower_string


def random_solarpark_observation_data() -> dict:
    data = {
        "name_of_model": "Test",
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "date_of_data": "2021-01-01",
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "avg_confidence": 100.0,
        "name_in_aws": "Test",
        "comment": "None",
        "lat": [599968.55, 599970.91, 599973.65, 599971.31, 599968.55],
        "lon": [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63],
        "geom": "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))",
    }
    return data


def random_solarpark_observation() -> SolarParkObservation:
    name_of_model = random_lower_string()
    date_of_data = date(2021, 1, 1)
    size_in_sq_m = 100.0
    peak_power = 100.0
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    comment = "None"
    lat = [599968.55, 599970.91, 599973.65, 599971.31, 599968.55]
    lon = [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63]
    geom = "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))"
    solarpark_observation = SolarParkObservation(
        name_of_model=name_of_model,
        date_of_data=date_of_data,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        comment=comment,
        lat=lat,
        lon=lon,
        geom=geom,
    )
    return solarpark_observation


def create_random_solarpark_observation(db: Session) -> SolarParkObservation:
    solarpark_observation_in = random_solarpark_observation()
    solarpark_observation = crud.solarpark_observation.create(
        db, obj_in=solarpark_observation_in, solarpark_id=1
    )
    return solarpark_observation
