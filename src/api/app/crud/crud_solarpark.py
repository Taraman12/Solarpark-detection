# build-in
from typing import Any, TypeVar

# third-party
# from pydantic import BaseModel
from shapely.geometry import Polygon
from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.models.solarpark import SolarPark
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate

# local modules
from .base import CRUDBase

# import shapely.wkt
# from geoalchemy2.elements import WKTElement
# from geoalchemy2.shape import to_shape


ModelType = TypeVar("ModelType", bound=Base)


class CRUDSolarPark(CRUDBase[SolarPark, SolarParkCreate, SolarParkUpdate]):
    def get(self, db: Session, id: Any, *, polygon: bool = False) -> SolarPark:
        if polygon:
            db_obj = db.query(SolarPark).filter(SolarPark.id == id).first()
            db_obj.geometry = Polygon(db_obj.geometry)
            return db_obj
        return db.query(SolarPark).filter(SolarPark.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, polygon: bool = False
    ) -> SolarPark:
        if polygon:
            db_obj = db.query(SolarPark).offset(skip).limit(limit).all()
            db_obj.geometry = Polygon(db_obj.geometry)
            return db_obj
        return db.query(SolarPark).offset(skip).limit(limit).all()

    # pass
    # def create(self, db: Session, *, obj_in: SolarParkCreate):
    #     polygon = Polygon(zip(obj_in.lon, obj_in.lat))
    #     geometry = WKTElement(polygon.wkt, srid=4326)
    #     print(geometry)
    #     db_obj = SolarPark(
    #         size_in_sq_m=obj_in.size_in_sq_m,
    #         peak_power=obj_in.peak_power,
    #         date_of_data=obj_in.date_of_data,
    #         first_detection=obj_in.first_detection,
    #         last_detection=obj_in.last_detection,
    #         geometry=geometry,
    #     )
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj

    # def create(self, db: Session, *, obj_in: SolarParkCreate):
    # print(obj_in.geometry)
    # polygon = shapely.wkt.loads(obj_in.geometry)
    # polygon = WKTElement(polygon)
    # #polygon = Polygon(obj_in.geometry)
    # #print(obj_in.geometry)
    # # wkt = f"POLYGON(({','.join([f'{lon} {lat}' for lat, lon in obj_in.geometry])}))"
    # # geometry = str(WKTElement(wkt, srid=4326))
    # #geometry = WKTElement(Polygon(obj_in.geometry))
    # #geometry = f"POLYGON(({','.join([f'{x[0]} {x[1]}' for x in obj_in.geometry])}))"
    # db_obj = SolarPark(
    #     size_in_sq_m=obj_in.size_in_sq_m,
    #     peak_power=obj_in.peak_power,
    #     date_of_data=obj_in.date_of_data,
    #     first_detection=obj_in.first_detection,
    #     last_detection=obj_in.last_detection,
    #     geometry=polygon,
    # )
    # db.add(db_obj)
    # db.commit()
    # db.refresh(db_obj)
    # return db_obj


solarpark = CRUDSolarPark(SolarPark)
