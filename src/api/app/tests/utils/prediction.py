from datetime import date

from sqlalchemy.orm import Session

from app import crud

# from app.core.config import settings
from app.models.prediction import Prediction
from app.tests.utils.utils import random_lower_string


def random_prediction_data() -> dict:
    data = {
        "name_of_model": "Test",
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "date_of_data": "2021-01-01",
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "avg_confidence": 100.0,
        "image_identifier": "Test",
        "comment": "None",
        "lat": [599968.55, 599970.91, 599973.65, 599971.31, 599968.55],
        "lon": [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63],
        "geom": "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))",
    }
    return data


def random_prediction() -> Prediction:
    name_of_model = random_lower_string()
    date_of_data = date(2021, 1, 1)
    size_in_sq_m = 100.0
    peak_power = 100.0
    avg_confidence = 100.0
    image_identifier = random_lower_string()
    comment = "None"
    lat = [599968.55, 599970.91, 599973.65, 599971.31, 599968.55]
    lon = [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63]
    geom = "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))"
    prediction = Prediction(
        name_of_model=name_of_model,
        date_of_data=date_of_data,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        avg_confidence=avg_confidence,
        image_identifier=image_identifier,
        comment=comment,
        lat=lat,
        lon=lon,
        geom=geom,
    )
    return prediction


# NOTE: id can be changed (should be automatically generated)
def create_random_prediction(db: Session) -> Prediction:
    prediction_in = random_prediction()
    prediction = crud.prediction.create(db, obj_in=prediction_in, solarpark_id=42)
    return prediction


# def random_prediction_update() -> PredictionUpdate:
