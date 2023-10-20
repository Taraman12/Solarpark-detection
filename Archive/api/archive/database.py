from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ToDo: Add a .env file to store the database credentials
# Setting for docker
# SQLALCHEMY_DATABASE_URL = "postgresql://hallo_api:hallo_api@db:5432/hallo_api_dev"
SQLALCHEMY_DATABASE_URL = (
    "postgresql://hallo_api:hallo_api@localhost:5432/hallo_api_dev"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
