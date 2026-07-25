from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

from typing import List

from pathlib import Path


BASE_DIR = Path('/.env')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR, env_nested_delimiter=None, env_file_encoding='utf-8', case_sensitive=True, extra='ignore')

    DEBUG: bool = False

    DATABASE_URL: str = Field(alias="DB_URL")
    ALLOWED_ORIGINS: str = Field(alias="ALLOW_ORIGINS")
    JWT_SECRET_KEY: str = Field(alias="JWT_SECRET_KEY")
    HASHING_ALGORITHM: str = Field(alias="HASHING_ALGORITHM")
    SSH_KEY: str = Field(alias="SSH_KEY")
    HMAC_SECRET_MESSAGE: str = Field(alias="HMAC_SECRET_MESSAGE")
    FERNET_KEY: str = Field(alias="FERNET")
    STORAGE_PATH: str = Field(alias="STORAGE_PATH")
    REDIS_PWD: str = Field(alias="REDIS_PWD")

    @classmethod
    @field_validator("ALLOWED_ORIGINS", mode='before')
    def validate_fields(cls, v: str) -> List[str]:
        try:
            result = v.split(',')
        except ValueError as V:
            raise V
        return result


setting = Settings()
