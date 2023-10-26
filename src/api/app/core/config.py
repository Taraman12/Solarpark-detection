# build-in
from typing import List, Optional, Union

# third-party
from pydantic import AnyHttpUrl, HttpUrl, field_validator  # PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ToDo: Revisit BACKEND_CORS_ORIGINS


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "localhost"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8080"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://3.66.239.204:80",
        "http://3.66.239.204",
        "http://localhost",
        "http://preprocessing:5678",
        "http://preprocessing",
        "http://localhost:80",
        "http://frontend:80",
        "http://localhost:8080",
        "http://frontend:8080",
        "http://frontend:5000",
        "http://localhost:5000",
        "http://localhost:5678",
        "http://preprocessing:5678",
        "http://ml-serve:8081",
        "http://localhost:8081",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Solar-Park-Detection"
    SENTRY_DSN: Optional[HttpUrl] = None

    HOST: str = "localhost"
    PORT: str = "5432"
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    DB: str = "solar-park-detection"

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", env_file=".env", case_sensitive=True
    )

    # SMTP_TLS: bool = True
    # SMTP_PORT: Optional[int] = None
    # SMTP_HOST: Optional[str] = None
    # SMTP_USER: Optional[str] = None
    # SMTP_PASSWORD: Optional[str] = None
    # EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    # EMAILS_FROM_NAME: Optional[str] = None


settings = Settings()
