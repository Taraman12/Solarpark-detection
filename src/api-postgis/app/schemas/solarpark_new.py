# build-in
from datetime import date
from typing import Any, List, Optional, Tuple, Union

from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from geojson_pydantic.geometries import Polygon
from pydantic import BaseConfig, BaseModel, validator

"""Minimum working example snippet for handling lat lng coordinates and geometry types using Fastapi"""

# app = FastAPI()


class SolarParkBase(BaseModel):
    name_of_model: str
    size_in_sq_m: float
    peak_power: float
    date_of_data: date
    first_detection: date
    last_detection: date
    avg_confidence: float
    lat: List[float]
    lon: List[float]
    geom: Polygon  # List[conlist(Position, min_items=4)]

    class Config(BaseConfig):
        arbitrary_types_allowed = True


class SolarPark(SolarParkBase):
    id: int

    class Config:
        orm_mode = True


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass


# https://gist.github.com/Sieboldianus/1d8f2f4b9d3519b640b695d62a28a6be
# class Coordinates(BaseModel):
#     lat: float = 0
#     lng: float = 0

#     @validator('lat')
#     def lat_within_range(cls, v):
#         if not -90 < v < 90:
#             raise ValueError('Latitude outside allowed range')
#         return v

#     @validator('lng')
#     def lng_within_range(cls, v):
#         if not -180 < v < 180:
#             raise ValueError('Longitude outside allowed range')
#         return v

# class UserIn(BaseModel):
#     username: str
#     coordinates: Coordinates

# class UserOut(BaseModel):
#     username: str
#     coordinates: Coordinates

# class UserInDB(BaseModel):
#     username: str
#     coordinates_geom: WKTElement

#     class Config(BaseConfig):
#         arbitrary_types_allowed = True

# # def get_geom_from_coordinates(coordinates: Coordinates):
# #     geom_wkte = WKTElement(f"Point ({coordinates.lng} {coordinates.lat})", srid=4326, extended=True)
# #     return geom_wkte

# # def get_coordinates_from_geom(geom: WKTElement):
# #     shply_geom = to_shape(geom)
# #     coordinates = Coordinates(lng=shply_geom.x, lat=shply_geom.y)
# #     return coordinates

# # def fake_save_user(user_in: UserIn):
# #     coordinates_geom = get_geom_from_coordinates(user_in.coordinates)
# #     user_in_db = UserInDB(**user_in.dict(), coordinates_geom=coordinates_geom)
# #     print("User saved! ..not really")
# #     return user_in_db

# # def fake_loaduser(user_saved: UserInDB):
# #     coordinates = get_coordinates_from_geom(user_saved.coordinates_geom)
# #     user_out = UserOut(**user_saved.dict(), coordinates=coordinates)
# #     print("User loaded! ..not really")
# #     return user_out

# # @app.post("/user/", response_model=UserOut)
# # async def create_user(*, user_in: UserIn):
# #     user_saved = fake_save_user(user_in)
# #     user_out = fake_loaduser(user_saved)
# #     return user_out
