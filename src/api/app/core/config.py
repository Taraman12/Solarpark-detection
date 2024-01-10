# build-in
import secrets
from typing import List, Optional, Union

# third-party
from pydantic import (  # PostgresDsn, validator
    AnyHttpUrl,
    EmailStr,
    Field,
    HttpUrl,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# ToDo: Revisit BACKEND_CORS_ORIGINS


class Settings(BaseSettings):
    # env_file: str = get_env_file()
    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        env_file=(".env", ".env.prod"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(secrets.token_urlsafe(32))  # secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # SERVER_NAME: str = "localhost"
    # used for email templates
    SERVER_HOST: AnyHttpUrl = "http://localhost:8080"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:5000",
        "http://localhost:5678",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://3.66.239.204:80",
        "http://3.66.239.204",
        "http://localhost",
        "http://preprocessing:5678",
        "http://preprocessing",
        "http://frontend:80",
        "http://frontend:8080",
        "http://frontend:5000",
        "http://preprocessing:5678",
        "http://ml-serve:8081",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="plain")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Solar-Park-Detection"
    SENTRY_DSN: Optional[HttpUrl] = None

    POSTGRES_HOST: str = Field("localhost")
    POSTGRES_PORT: str = Field("5432")
    POSTGRES_USER: str = Field("postgres")
    POSTGRES_PASSWORD: str = Field("postgres")
    POSTGRES_DB: str = Field("solar-park-detection")

    FIRST_SUPERUSER: EmailStr = Field("example@mail.com")  # John@doe.com
    FIRST_SUPERUSER_PASSWORD: str = Field("password")
    USERS_OPEN_REGISTRATION: bool = False

    EMAILS_ENABLED: bool = False

    DOCKER_SWARM_MANAGER_IP: str = Field("ip-address")
    DOCKER_SWARM_JOIN_TOKEN_MANAGER: str = Field("Manager-Token")
    DOCKER_SWARM_JOIN_TOKEN_WORKER: str = Field("Worker-Token")

    # SMTP_TLS: bool = True
    # SMTP_PORT: Optional[int] = None
    # SMTP_HOST: Optional[str] = None
    # SMTP_USER: Optional[str] = None
    # SMTP_PASSWORD: Optional[str] = None
    # EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    # EMAILS_FROM_NAME: Optional[str] = None


settings = Settings()
