# third-party
from geoalchemy2 import Geometry
from sqlalchemy import ARRAY, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# from sqlalchemy import event

# local modules
from app.db.base_class import Base


class SolarParkObservation(Base):
    id = Column(Integer, primary_key=True, index=True)
    solarpark_id = Column(Integer, ForeignKey("solarpark.id", ondelete="CASCADE"))
    name_of_model = Column(String)
    size_in_sq_m = Column(Float)
    peak_power = Column(Float)
    date_of_data = Column(Date)
    avg_confidence = Column(Float)
    name_in_aws = Column(String)
    is_valid = Column(String, default="None")
    comment = Column(String, default="None")
    lat = Column(ARRAY(Float))
    lon = Column(ARRAY(Float))
    geom = Column(Geometry("POLYGON", srid=4326))

    solarpark = relationship("SolarPark", back_populates="observations")


# @event.listens_for(SolarParkObservation, "after_insert")
# def receive_after_insert(mapper, connection, target):
#     # update solarpark
