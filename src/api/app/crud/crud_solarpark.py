# local modules
from .base import CRUDBase
from app.models.solarpark import SolarPark
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate


class CRUDSolarPark(CRUDBase[SolarPark, SolarParkCreate, SolarParkUpdate]):
    pass


solarpark = CRUDSolarPark(SolarPark)
