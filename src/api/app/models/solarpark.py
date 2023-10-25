# third-party
from geoalchemy2 import Geometry
from sqlalchemy import ARRAY, Column, Date, Float, Integer, String
from sqlalchemy.orm import relationship

# local modules
from app.db.base_class import Base


class SolarPark(Base):
    # Tablename will be generated automatically (see Base class)
    # __tablename__ = "solarpark"

    id = Column(Integer, primary_key=True, index=True)
    name_of_model = Column(ARRAY(String))
    size_in_sq_m = Column(Float)
    peak_power = Column(Float)
    date_of_data = Column(Date)
    first_detection = Column(Date)
    last_detection = Column(Date)
    avg_confidence_over_all_observations = Column(Float)
    name_in_aws = Column(String)
    is_valid = Column(String, default="None")
    comment = Column(String, default="None")
    lat = Column(ARRAY(Float))
    lon = Column(ARRAY(Float))
    geom = Column(Geometry("POLYGON", srid=4326))  # Column(String)

    observations = relationship("SolarParkObservation", back_populates="solarpark")
