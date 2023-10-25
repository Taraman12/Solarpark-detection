# local modules
from fastapi.encoders import jsonable_encoder
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.models.solarpark_observation import SolarParkObservation
from app.schemas.solarpark_observation import (
    SolarParkObservationCreate,
    SolarParkObservationUpdate,
)

from .base import CRUDBase


class CRUDSolarParkObservation(
    CRUDBase[
        SolarParkObservation, SolarParkObservationCreate, SolarParkObservationUpdate
    ]
):
    def get(self, db: Session, *, id: int) -> SolarParkObservation:
        db_obj = (
            db.query(SolarParkObservation).filter(SolarParkObservation.id == id).first()
        )
        if db_obj is None:
            return None

        if isinstance(db_obj.geom, str):
            db_obj.geom = WKTElement(db_obj.geom)
        db_obj.geom = to_shape(db_obj.geom).wkt
        return db_obj

    def create(
        self, db: Session, *, obj_in: SolarParkObservationCreate, solarpark_id: int
    ) -> SolarParkObservation:
        # print(obj_in)
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = SolarParkObservation(**obj_in_data)  # type: ignore
        db_obj.solarpark_id = solarpark_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        # print("here")
        db_obj.geom = to_shape(db_obj.geom).wkt
        # print(db_obj.__dict__)
        return db_obj

    def get_multi_by_solarpark_id(self, db: Session, *, solarpark_id: int):
        db_obj = (
            db.query(SolarParkObservation)
            .filter(SolarParkObservation.solarpark_id == solarpark_id)
            .all()
        )
        if db_obj is None:
            return None

        for obj in db_obj:
            if isinstance(obj.geom, str):
                obj.geom = WKTElement(obj.geom)
            obj.geom = to_shape(obj.geom).wkt
        return db_obj


solarpark_observation = CRUDSolarParkObservation(SolarParkObservation)
