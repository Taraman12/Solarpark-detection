# build-in
from datetime import date
from enum import Enum

# from geoalchemy2.types import Geometry
# from geoalchemy2 import WKTElement
from typing import List

# third-party
from pydantic import BaseModel


class Status(str, Enum):
    none = "None"
    valid = "valid"
    non_valid = "non-valid"
    unsure = "unsure"


class SolarParkBase(BaseModel):
    name_of_model: str
    size_in_sq_m: float
    peak_power: float
    date_of_data: date
    first_detection: date
    last_detection: date
    avg_confidence: float
    name_in_aws: str
    is_valid: Status = Status.none
    comment: str = "None"
    lat: List[float]
    lon: List[float]

    class Config:
        orm_mode = True
        # use_enum_values = True


class SolarPark(SolarParkBase):
    id: int


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass
