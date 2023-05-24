# third-party
from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, Float, Integer, String

# local modules
from app.db.base_class import Base

# from sqlalchemy.orm import relationship


class SolarPark(Base):
    # Tablename will be generated automatically (see Base class)
    # __tablename__ = "solar_plants"

    id = Column(Integer, primary_key=True, index=True)
    size_in_sq_m = Column(Float)
    peak_power = Column(Float)
    date_of_data = Column(Date)
    first_detection = Column(Date)
    last_detection = Column(Date)
    geometry = Column(String)  # Column(Geometry("POLYGON", srid=4326))
