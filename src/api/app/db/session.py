# third-party
from functools import lru_cache
from typing import Optional

from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# local modules
from app.core.config import settings


# see: https://fastapi.tiangolo.com/advanced/settings/?h=envir
@lru_cache()
def get_settings():
    return settings


SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = PostgresDsn.build(
    scheme="postgresql",
    username=settings.USER,
    password=settings.PASSWORD,
    host=settings.HOST,
    path=settings.DB,
)

engine = create_engine(SQLALCHEMY_DATABASE_URI.unicode_string(), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
