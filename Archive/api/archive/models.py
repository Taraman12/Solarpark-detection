from sqlalchemy import Column, Date, Float, Integer, String

from .database import Base

# from sqlalchemy.orm import relationship


class SolarPlants(Base):
    __tablename__ = "solar_plants"

    id_plant = Column(Integer, primary_key=True, index=True)
    size_in_sq_m = Column(Float)
    peak_power = Column(Float)
    date_of_data = Column(Date)
    first_detection = Column(Date)
    last_detection = Column(Date)
    geometry = Column(String, unique=True)


class MailList(Base):
    __tablename__ = "mail_list"

    id_mail = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
