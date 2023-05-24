# build-in
import os
from os.path import abspath, dirname, join
from typing import Any, Dict, List, Optional, Union

# third-party
from dotenv import load_dotenv
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, PostgresDsn, validator

# import secrets


# ToDo: Revisit BACKEND_CORS_ORIGINS


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8080"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:8080",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Solar-Park-Detection"
    SENTRY_DSN: Optional[HttpUrl] = None

    # @validator("SENTRY_DSN", pre=True)
    # def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
    #     if len(v) == 0:
    #         return None
    #     return v
    def get_src_path():
        current_path = abspath(__file__)
        src_path = None
        while current_path != "/":
            current_path = dirname(current_path)
            if os.path.exists(join(current_path, "src")):
                src_path = join(current_path, "src")
                return src_path

    if not os.getenv("DOCKERIZED"):
        src_path = get_src_path()
        dotenv_path = join(src_path, ".env")
        load_dotenv(dotenv_path)

    # if not DOCKERIZED override .env server db with localhost
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "solar-park-detection")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # SMTP_TLS: bool = True
    # SMTP_PORT: Optional[int] = None
    # SMTP_HOST: Optional[str] = None
    # SMTP_USER: Optional[str] = None
    # SMTP_PASSWORD: Optional[str] = None
    # EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    # EMAILS_FROM_NAME: Optional[str] = None


settings = Settings()
