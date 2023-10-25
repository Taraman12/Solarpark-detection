# build-in
import json
from typing import Any, Dict, TypeVar, Union

# third-party
from fastapi import File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape

# from geoalchemy2.types import WKBElement
from geojson import Feature, FeatureCollection, Polygon
from shapely.geometry import shape

# from sqlalchemy import func
from sqlalchemy.orm import Session

from app.cloud.logging_config import get_logger

# local modules
from app.db.base_class import Base
from app.models.solarpark import SolarPark
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate

from .base import CRUDBase

# import shapely.wkt


logger = get_logger("BaseConfig")
# import geojson
# from geoalchemy2.shape import to_shape
# import shapely.wkt
# from geoalchemy2.elements import WKTElement
# from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Base)


# send geojson-file as stream
def generate(feature_collection: FeatureCollection):
    yield '{"type": "FeatureCollection", "features": ['
    for i, feature in enumerate(feature_collection["features"]):
        if i > 0:
            yield ","
        yield str(feature)
    yield "]}"


class CRUDSolarPark(CRUDBase[SolarPark, SolarParkCreate, SolarParkUpdate]):
    def get(self, db: Session, *, id: int) -> SolarPark:
        db_obj = db.query(SolarPark).filter(SolarPark.id == id).first()
        if db_obj is None:
            return None

        if isinstance(db_obj.geom, str):
            db_obj.geom = WKTElement(db_obj.geom)
        db_obj.geom = to_shape(db_obj.geom).wkt
        return db_obj

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> SolarPark:
        db_obj = db.query(SolarPark).offset(skip).limit(limit).all()
        if db_obj is None:
            return None

        for obj in db_obj:
            if isinstance(obj.geom, str):
                obj.geom = WKTElement(obj.geom)
            obj.geom = to_shape(obj.geom).wkt
        return db_obj
        # return db.query(SolarPark).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: SolarParkCreate) -> SolarPark:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = SolarPark(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.geom = to_shape(db_obj.geom).wkt
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: SolarPark,
        obj_in: Union[SolarParkUpdate, Dict[str, Any]],
    ) -> SolarPark:
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
        db_obj = db.query(SolarPark).all()
        obj_data = jsonable_encoder(db_obj)
        # GeoJSON-FeatureCollection erstellen
        features = []
        for row in obj_data:
            lat = row["lat"]
            lon = row["lon"]
            coords = [(lon[i], lat[i]) for i in range(len(lat))]
            polygon = Polygon([coords])
            properties = {
                "name_of_model": row["name_of_model"],
                "size_in_sq_m": row["size_in_sq_m"],
                "peak_power": row["peak_power"],
                "date_of_data": row["date_of_data"],  # .strftime('%Y-%m-%d'),
                "first_detection": row["first_detection"],  # .strftime('%Y-%m-%d'),
                "last_detection": row["last_detection"],  # .strftime('%Y-%m-%d'),
                "avg_confidence": row["avg_confidence"],
                "name_in_aws": row["name_in_aws"],
                "is_valid": row["is_valid"],
                "comment": row["comment"],
            }
            feature = Feature(geometry=polygon, properties=properties)
            features.append(feature)
        feature_collection = FeatureCollection(features)

        # GeoJSON-Datei als Stream senden
        async def generate():
            yield '{"type": "FeatureCollection", "features": ['
            for i, feature in enumerate(feature_collection["features"]):
                if i > 0:
                    yield ","
                yield str(feature)
            yield "]}"

        # geojson_data = str(feature_collection).encode("utf-8")
        # response.headers["Content-Disposition"] = "attachment; filename=geodata.geojson"
        return StreamingResponse(
            content=generate(),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=solar-parks.geojson"},
        )

    async def create_upload_file(
        self,
        db: Session,
        file: UploadFile = File(...),
    ) -> Any:
        contents = await file.read()

        data = json.loads(contents)
        # print(data)
        for feature in data["features"]:
            polygon = shape(feature["geometry"])
            # print(polygon)
            coords = polygon.exterior.coords
            # Extract the latitude and longitude coordinates into separate lists
            latitudes = [coord[1] for coord in coords]
            longitudes = [coord[0] for coord in coords]
            properties = feature["properties"]
            obj_in_data = SolarPark(
                name_of_model=properties["name_of_model"],
                size_in_sq_m=properties["size_in_sq_m"],
                peak_power=properties["peak_power"],
                date_of_data=properties["date_of_data"],
                first_detection=properties["first_detection"],
                last_detection=properties["last_detection"],
                avg_confidence=properties["avg_confidence"],
                name_in_aws=properties["name_in_aws"],
                is_valid=properties["is_valid"],
                comment=properties["comment"],
                lat=latitudes,
                lon=longitudes,
            )
            db.add(obj_in_data)
            logger.info(f"Added {obj_in_data.name_in_aws} to database")
            db.commit()

        # db.commit()
        return {"filename": file.filename}

    def check_overlap(self, db: Session, *, obj_in: SolarParkCreate) -> bool:
        # print(WKTElement(obj_in.geom))

        # db_obj = db.query(SolarPark).filter(SolarPark.geom.intersects(WKTElement(obj_in.geom))).first()
        db_obj = (
            db.query(SolarPark)
            .filter(SolarPark.geom.intersects(WKTElement(obj_in.geom)))
            .first()
        )
        # print(db_obj.__dict__)
        print(db_obj.id)
        if db_obj is None:
            return None
        else:
            # here the unique id of the solarpark is returned
            return db_obj

        # print(to_shape(db_obj.geom))
        # print("Hello")
        # # query = db.query(SolarPark).filter(SolarPark.geom.ST_Area() > 0).one()
        # # print(query.id)
        # # result = db.execute(existing_solarpark)
        # #query = db.query(SolarPark).filter(SolarPark.geom.ST_Overlaps(WKTElement("POLYGON ((599968.55 5570202.63, 599970.90 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))")))
        # #print(query)
        # # result = db.execute(existing_solarpark)
        # # print(result)
        # for row in query:
        #     print(row.id)
        # return existing_solarpark

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
