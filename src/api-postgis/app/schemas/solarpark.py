# build-in
from datetime import date
from typing import Any, List, Optional, Tuple, Union

from geoalchemy2 import WKTElement
from geoalchemy2.types import Geometry

# third-party
from pydantic import (  # ConstrainedFloat, Field, PrivateAttr, conlist
    BaseConfig,
    BaseModel,
    Field,
    validator,
)

"""
Related Links:
https://github.com/tiangolo/fastapi/issues/315
https://github.com/tiangolo/fastapi/issues/1246

Solution could be to use a custom response model for each input and output:
https://fastapi.tiangolo.com/tutorial/response-model/
"""


# from shapely.geometry import Polygon, mapping
# from shapely.wkt import loads

# class Latitude(ConstrainedFloat):
#     ge = -90
#     le = 90


# class Longitude(ConstrainedFloat):
#     ge = -180
#     le = 180


# class RawPolygon(BaseModel):
#     __root__: conlist(conlist(Tuple[Latitude, Longitude], min_items=3), min_items=1)
#     _polygon: Polygon = PrivateAttr()

#     def __init__(self, **data: Any):
#         super().__init__(**data)
#         self._polygon = Polygon(data["__root__"][0], data["__root__"][1:])

#     @property
#     def polygon(self) -> Polygon:
#         return self._polygon

# from typing import List, Tuple, Union
# from pydantic.dataclasses import dataclass


# @dataclass
# class Geometry:
#     type: str
#     coordinates: List[Union[Tuple[float, float], Tuple[float, float, float]]]
class Coordinates(BaseModel):
    lat: float = 0
    lng: float = 0

    @validator("lat")
    def lat_within_range(cls, v):
        if not -90 < v < 90:
            raise ValueError("Latitude outside allowed range")
        return v

    @validator("lng")
    def lng_within_range(cls, v):
        if not -180 < v < 180:
            raise ValueError("Longitude outside allowed range")
        return v


class UserIn(BaseModel):
    username: str
    coordinates: Coordinates


class UserOut(BaseModel):
    username: str
    coordinates: Coordinates


class UserInDB(BaseModel):
    username: str
    coordinates_geom: WKTElement

    class Config(BaseConfig):
        arbitrary_types_allowed = True


# class Position(BaseModel):
#     Position = Union[Tuple[float, float], Tuple[float, float, float]]


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
    geom: WKTElement  # List[conlist(Position, min_items=4)]

    class Config(BaseConfig):
        arbitrary_types_allowed = True

    # @validator("geom", pre=True, always=True)
    # def assemble_geometry(cls, v, values):
    #     pass
    # print(values)

    # use_enum_values = True
    # Any # = Field(sa_column=Geometry(geometry_type='POLYGON', srid=4326))

    # lat: List[float]=0
    # lon: List[float]=0
    # geometry: str #List[Tuple[float, float]] # List[List[float], List[float]]
    # @property
    # def geometry(self) -> Polygon:
    #     # Create a Polygon object from the coordinates
    #     return Polygon(zip(self.longitude, self.latitude))
    # @property
    # def polygon(self) -> Polygon:
    #     # Load the Polygon object from the WKT string
    #     return loads(self.geometry)

    # @property
    # def polygon_wkt(self) -> str:
    #     # Return the WKT representation of the Polygon object
    #     return mapping(self.polygon).to_wkt()


class SolarPark(SolarParkBase):
    id: int

    class Config:
        orm_mode = True
        # use_enum_values = True


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass
