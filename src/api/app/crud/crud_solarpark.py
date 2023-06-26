# build-in
import json
from typing import Any, TypeVar

# third-party
from fastapi import File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from geojson import Feature, FeatureCollection, Polygon
from shapely.geometry import shape


# local modules
from app.db.base_class import Base
from app.models.solarpark import SolarPark
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate
from .base import CRUDBase

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
    # super().__init__(model=SolarPark)
    # def create(self, db):
    #     # check if SolarPark already exists
    #     # if not, create new SolarPark
    #     query = get_multi()

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

        db.commit()
        return {"filename": file.filename}

    # def get(self, db: Session, id: Any, *, polygon: bool = False) -> SolarPark:
    #     if polygon:
    #         db_obj = db.query(SolarPark).filter(SolarPark.id == id).first()
    #         db_obj.geometry = Polygon(db_obj.geometry)
    #         return db_obj
    #     return db.query(SolarPark).filter(SolarPark.id == id).first()

    # def get_multi(
    #     self, db: Session, *, skip: int = 0, limit: int = 100, polygon: bool = False
    # ) -> SolarPark:
    #     if polygon:
    #         db_obj = db.query(SolarPark).offset(skip).limit(limit).all()
    #         db_obj.geometry = Polygon(db_obj.geometry)
    #         return db_obj
    #     return db.query(SolarPark).offset(skip).limit(limit).all()

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
