from datetime import date

from pydantic import BaseModel


class SolarPlantsBase(BaseModel):
    size_in_sq_m: float
    peak_power: float
    date_of_data: date
    first_detection: date
    last_detection: date
    geometry: str


class SolarPlantsCreate(SolarPlantsBase):
    pass


class SolarPlants(SolarPlantsBase):
    id_plant: int

    class Config:
        orm_mode = True


class MailListBase(BaseModel):
    email: str

    class Config:
        orm_mode = True


class MailListCreate(MailListBase):
    pass


class MailList(MailListBase):
    id_mail: int

    class Config:
        orm_mode = True
