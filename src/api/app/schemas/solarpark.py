# build-in
from datetime import date

# third-party
from pydantic import BaseModel
# from geoalchemy2.types import Geometry
# from geoalchemy2 import WKTElement
from typing import List


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


class SolarPark(SolarParkBase):
    id: int

    class Config:
        orm_mode = True
        # use_enum_values = True


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass
