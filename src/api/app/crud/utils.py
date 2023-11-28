from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.models.solarpark import SolarPark
from app.schemas.solarpark_observation import SolarParkObservationCreate


def check_overlap(db: Session, obj_in: SolarParkObservationCreate) -> SolarPark:
    db_obj = (
        db.query(SolarPark)
        .filter(SolarPark.geom.intersects(WKTElement(obj_in.geom)))
        .first()
    )
    if db_obj is None:
        return None

    if isinstance(db_obj.geom, str):
        db_obj.geom = WKTElement(db_obj.geom)
    db_obj.geom = to_shape(db_obj.geom).wkt
    return db_obj


# return (
#     db.query(SolarPark)
#     .filter(SolarPark.geom.intersects(WKTElement(obj_in.geom)))
#     .first()
# )


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
