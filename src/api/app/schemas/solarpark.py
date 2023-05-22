# build-in
from datetime import date

# third-party
from pydantic import BaseModel


class SolarParkBase(BaseModel):
    size_in_sq_m: float
    peak_power: float
    date_of_data: date
    first_detection: date
    last_detection: date
    geometry: str


class SolarPark(SolarParkBase):
    id: int

    class Config:
        orm_mode = True


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass
