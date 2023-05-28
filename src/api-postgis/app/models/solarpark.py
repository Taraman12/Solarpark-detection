# third-party
from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, Float, Integer, String, ARRAY

# local modules
from app.db.base_class import Base

# from sqlalchemy.orm import relationship


class SolarPark(Base):
    # Tablename will be generated automatically (see Base class)
    # __tablename__ = "solar_plants"

    id = Column(Integer, primary_key=True, index=True)
    name_of_model = Column(String)
    size_in_sq_m = Column(Float)
    peak_power = Column(Float)
    date_of_data = Column(Date)
    first_detection = Column(Date)
    last_detection = Column(Date)
    avg_confidence = Column(Float)
    lat = Column(ARRAY(item_type=Float))
    lon = Column(ARRAY(item_type=Float))
    geom = Column(Geometry("POLYGON", srid=4326))  # Column(String)
