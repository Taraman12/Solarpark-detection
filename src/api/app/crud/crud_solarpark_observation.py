from typing import Any, Dict, Union

# local modules
from fastapi import File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from geoalchemy2 import WKTElement, WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session
from geoalchemy2 import functions
from geojson import Feature, FeatureCollection, Polygon

# from geoalchemy2.shape import InvalidShapeError
from app.models.solarpark_observation import SolarParkObservation
from app.schemas.solarpark_observation import (
    SolarParkObservationCreate,
    SolarParkObservationUpdate,
)

from .base import CRUDBase

"""
see:
https://gis.stackexchange.com/questions/233184/converting-geoalchemy2-elements-wkbelement-to-wkt
https://stackoverflow.com/questions/77353137/retrieve-postgis-geometry-data-as-wkt-using-geoalchemy-without-making-extra-quer

right now, the geom column is either a WKBElement or a string
This is due to the test in api, where the geom is a dict and wouldn't be converted to a WKBElement
fix this in the future, so that the geom is always a WKBElement
"""


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
        # db_obj.geom = functions.ST_AsText(db_obj.geom)
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
                .offset(skip)
                .limit(limit)
                .all()
            )

        if not db_obj:
            return db_obj

        for obj in db_obj:
            # try:
            #     obj.geom = functions.ST_AsText(obj.geom)
            # except Exception as e:
            #     raise ValueError(f"Invalid WKT format: {obj.geom}")

            # If obj.geom is already a WKBElement, convert it to WKT format
            if isinstance(obj.geom, WKBElement):
                obj.geom = to_shape(obj.geom).wkt
                continue

            # If obj.geom is a string, try to convert it to a WKTElement
            # ? maybe check if the string is a valid WKT format?
            if isinstance(obj.geom, str):
                # try:
                #     # obj.geom = functions.ST_AsText(obj.geom)
                #     obj.geom = WKTElement(obj.geom).wkt
                #     # obj.geom = to_shape(obj.geom).wkt
                # except Exception as e:
                #     raise ValueError(
                #         f"Invalid WKT format: {obj.geom} and type {type(obj.geom).__name__}"
                #     )
                continue

            # If obj.geom is neither a WKBElement nor a string, raise an error
            raise TypeError(f"Unexpected type {type(obj.geom).__name__} for obj.geom")

        return db_obj

    def create(
        self, db: Session, *, obj_in: SolarParkObservationCreate, solarpark_id: int
    ) -> SolarParkObservation:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = SolarParkObservation(**obj_in_data)  # type: ignore
        db_obj.solarpark_id = solarpark_id
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        db_obj.geom = to_shape(db_obj.geom).wkt
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
        # https://gis.stackexchange.com/questions/233184/converting-geoalchemy2-elements-wkbelement-to-wkt/233246#233246?newreg=a18c8fcff5e245fda8395530e9933b85
        db_obj = db.query(SolarParkObservation).all()
        print("db_obj", db_obj)
        if db_obj is None:
            return None

        # obj_data = jsonable_encoder(db_obj)

        # create GeoJSON-FeatureCollection
        features = []
        # print("obj_data", db_obj)
        for obj in db_obj:
            row = obj.__dict__
            print("row", row)
            # geom = functions.ST_AsGeoJSON(row["geom"])
            # geom = Polygon(row["geom"])
            if isinstance(row["geom"], str):
                geom = WKTElement(row["geom"])
                geom = to_shape(geom)
            else:
                geom = to_shape(row["geom"])
            properties = {
                "name_of_model": row["name_of_model"],
                "size_in_sq_m": row["size_in_sq_m"],
                "peak_power": row["peak_power"],
                "date_of_data": row["date_of_data"],  # .strftime('%Y-%m-%d'),
                "avg_confidence": row["avg_confidence"],
                "name_in_aws": row["name_in_aws"],
                "is_valid": row["is_valid"],
                "comment": row["comment"],
            }
            feature = Feature(geometry=geom, properties=properties)
            features.append(feature)
        feature_collection = FeatureCollection(features)

        # GeoJSON-File as stream
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
        for feature in data["features"]:
            polygon = shape(feature["geometry"])
            coords = polygon.exterior.coords
            # Extract the latitude and longitude coordinates into separate lists
            latitudes = [coord[1] for coord in coords]
            longitudes = [coord[0] for coord in coords]
            properties = feature["properties"]
            obj_in_data = SolarParkObservation(
                name_of_model=properties["name_of_model"],
                size_in_sq_m=properties["size_in_sq_m"],
                peak_power=properties["peak_power"],
                date_of_data=properties["date_of_data"],
                avg_confidence=properties["avg_confidence"],
                name_in_aws=properties["name_in_aws"],
                is_valid=properties["is_valid"],
                comment=properties["comment"],
                lat=latitudes,
                lon=longitudes,
                geom=polygon,
            )
            db.add(obj_in_data)
            logger.info(f"Added {obj_in_data.name_in_aws} to database")
            db.commit()

        # db.commit()
        return {"filename": file.filename}

    def delete(self, db: Session, *, id: int) -> SolarParkObservation:
        db_obj = db.query(SolarParkObservation).filter(SolarParkObservation.id == id)
        if db_obj is None:
            return None
        db_obj.delete()
        db.commit()
        return db_obj

    # ! danger zone (development only)
    def remove_all(self, db: Session) -> SolarParkObservation:
        db_obj = db.query(SolarParkObservation)
        if db_obj is None:
            return None
        db_obj.delete()
        db.commit()
        return db_obj


solarpark_observation = CRUDSolarParkObservation(SolarParkObservation)
