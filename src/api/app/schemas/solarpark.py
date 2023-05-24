# build-in
from datetime import date
from typing import Any, List, Optional, Tuple

# third-party
from pydantic import BaseModel, ConstrainedFloat, Field, PrivateAttr, conlist
from shapely.geometry import Polygon, mapping
from shapely.wkt import loads

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


class SolarParkBase(BaseModel):
    size_in_sq_m: float
    peak_power: float
    date_of_data: date
    first_detection: date
    last_detection: date
    geometry: str

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
