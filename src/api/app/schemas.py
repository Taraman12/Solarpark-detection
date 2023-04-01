from datetime import datetime

from pydantic import BaseModel


class SolarPlants(BaseModel):
    id_plant: int
    size_in_sq_m: float
    peak_power: float
    date_of_data: datetime.date
    first_detection: datetime.date
    last_detection: datetime.date
    geometry: str

    class Config:
        orm_mode = True


class SolarPlantsCreate(BaseModel):
    size_in_sq_m: float
    peak_power: float
    date_of_data: datetime.date
    first_detection: datetime.date
    last_detection: datetime.date
    geometry: str
