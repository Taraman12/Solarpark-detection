# third-party
from functools import lru_cache
from typing import Optional

from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# local modules
from app.core.config import settings


# see: https://fastapi.tiangolo.com/advanced/settings/?h=envir
# @lru_cache()
# def get_settings():
#     return settings


SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = PostgresDsn.build(
    scheme="postgresql",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host="localhost",  # settings.POSTGRES_HOST,  # set to localhost if parsing error local
    path=settings.POSTGRES_DB,
)

engine = create_engine(SQLALCHEMY_DATABASE_URI.unicode_string(), pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
