from typing import Any
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, EmailStr

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./mydb.db"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "mail@mail.com"
    MAIL_PASSWORD: str = "12345678"
    MAIL_FROM: str = "mail@mail.com"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "postgres"
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")

config = Settings()
