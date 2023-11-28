from typing import Generator, Dict

import pytest
from fastapi.testclient import TestClient

# from app.api_core.deps import get_db
# from app.core.config import settings
# from app.db.base_class import Base
from app.db.session import SessionLocal
from app.main import app
from app.tests.utils.utils import get_superuser_token_headers

# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session, sessionmaker


# @pytest.fixture(scope="session")
# def db() -> Generator[Session, None, None]:
#     engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
#     Base.metadata.create_all(bind=engine)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#     # override the original get_db
#     app.main.get_db = SessionLocal

#     db = SessionLocal()
#     yield db

#     # teardown
#     db.close()
#     Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


# @pytest.fixture(scope="session")
# def db():
#     Base.metadata.create_all(bind=engine)
#     yield
#     Base.metadata.drop_all(bind=engine)

# app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_superuser_token_headers(client)
