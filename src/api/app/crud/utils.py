from typing import Any

from geoalchemy2 import WKTElement
from sqlalchemy.orm import Session

from app.models.solarpark import SolarPark
from app.schemas.solarpark_observation import SolarParkObservationCreate


def check_overlap(db: Session, obj_in: SolarParkObservationCreate) -> Any:
    return (
        db.query(SolarPark)
        .filter(SolarPark.geom.intersects(WKTElement(obj_in.geom)))
        .first()
    )


def transform_solarpark_observation(
    solarpark_observation_in: SolarParkObservationCreate,
):
    solarpark_in = vars(solarpark_observation_in).copy()
    unwanted_keys = ["name_of_model", "avg_confidence", "date_of_data"]
    for key in unwanted_keys:
        solarpark_in.pop(key, None)
    solarpark_in["name_of_model"] = [solarpark_observation_in.name_of_model]
    solarpark_in["first_detection"] = solarpark_observation_in.date_of_data
    solarpark_in["last_detection"] = solarpark_observation_in.date_of_data
    solarpark_in[
        "avg_confidence_over_all_observations"
    ] = solarpark_observation_in.avg_confidence
    return solarpark_in
