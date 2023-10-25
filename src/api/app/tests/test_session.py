# third-party
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool

# # local modules
# from app.core.config import settings

# SQLALCHEMY_DATABASE_URI = "postgresql://"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URI,
#     # settings.SQLALCHEMY_DATABASE_URI,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )

# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base.metadata.create_all(bind=engine)


# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()


# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)
