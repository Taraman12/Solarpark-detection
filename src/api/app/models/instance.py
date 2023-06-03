from sqlalchemy import Column, Integer, String

# local modules
from app.db.base_class import Base

# from sqlalchemy.orm import relationship


class Instance(Base):
    # Tablename will be generated automatically (see Base class)

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    service = Column(String, unique=True)
    ec2_instance_id = Column(String)
