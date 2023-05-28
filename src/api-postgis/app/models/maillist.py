# third-party
from sqlalchemy import Column, Integer, String

# local modules
from app.db.base_class import Base


class MailList(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
