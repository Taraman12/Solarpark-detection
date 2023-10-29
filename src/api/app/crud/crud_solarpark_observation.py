from typing import Any, Dict, Union

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

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10000,
        solarpark_id: int = None,
    ) -> SolarParkObservation:
        # db_obj = db.query(SolarParkObservation).offset(skip).limit(limit).all()

        if solarpark_id is None:
            db_obj = db.query(SolarParkObservation).offset(skip).limit(limit).all()
        else:
            db_obj = (
                db.query(SolarParkObservation)
                .filter(SolarParkObservation.solarpark_id == solarpark_id)
                .all()
            )
        if not db_obj:
            return db_obj

        db_obj = [
            obj if not isinstance(obj.geom, str) else WKTElement(obj.geom)
            for obj in db_obj
        ]
        for obj in db_obj:
            obj.geom = to_shape(obj.geom).wkt
        return db_obj

    # def get_multi_by_solarpark_id(self, db: Session, *, solarpark_id: int):
    #         db_obj = (
    #             db.query(SolarParkObservation)
    #             .filter(SolarParkObservation.solarpark_id == solarpark_id)
    #             .all()
    #         )
    #         if db_obj is None:
    #             return None

    #         for obj in db_obj:
    #             if isinstance(obj.geom, str):
    #                 obj.geom = WKTElement(obj.geom)
    #             obj.geom = to_shape(obj.geom).wkt
    #         return db_obj

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

    def update(
        self,
        db: Session,
        *,
        db_obj: SolarParkObservation,
        obj_in: Union[SolarParkObservationUpdate, Dict[str, Any]],
    ) -> SolarParkObservation:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.geom = to_shape(db_obj.geom).wkt
        return db_obj

    def get_as_geojson(
        self,
        db: Session,
    ) -> Any:
        db_obj = db.query(SolarParkObservation).all()
        if db_obj is None:
            return None

        for obj in db_obj:
            if isinstance(obj.geom, str):
                obj.geom = WKTElement(obj.geom)
            obj.geom = to_shape(obj.geom).wkt
        return db_obj

    def delete(self, db: Session, *, id: int) -> SolarParkObservation:
        db_obj = db.query(SolarParkObservation).filter(SolarParkObservation.id == id)
        if db_obj is None:
            return None
        db_obj.delete()
        db.commit()
        return db_obj


solarpark_observation = CRUDSolarParkObservation(SolarParkObservation)
