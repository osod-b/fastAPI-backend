from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

from typing import List

from pathlib import Path


BASE_DIR = Path('/.env')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR, env_nested_delimiter=None, env_file_encoding='utf-8', case_sensitive=True, extra='ignore')

    DEBUG: bool = False

    ALLOWED_ORIGINS: str = Field(alias="ALLOW_ORIGINS")
    DATABASE_URL: str = Field(alias="DB_URL")
    CACHE_DB_URL: str = Field(alias="CACHE_DB_URL")
    JWT_SECRET_KEY: str = Field(alias="JWT_SECRET_KEY")
    TOKEN_EXPIRES_MINUTES: int = Field(alias="TOKEN_EXPIRES_MINUTES")
    TOKEN_EXPIRES_DAYS: int = Field(alias="TOKEN_EXPIRES_DAYS")
    HASHING_ALGORITHM: str = Field(alias="HASHING_ALGORITHM")
    SSH_KEY: str = Field(alias="SSH_KEY")
    HMAC_MESSAGE: str = Field(alias="HMAC_MESSAGE")
    ALLOWED_FILE_FORMATS: str = Field(alias="ALLOWED_FILE_FORMATS")
    ALLOWED_TABLE_NAMES: str = Field(alias="TABLES")
    ALLOWED_MEDIAS: str = Field(alias="ALLOWED_MEDIA")

    @classmethod
    @field_validator("ALLOWED_ORIGINS", "ALLOWED_FILE_FORMATS", "ALLOWED_TABLE_NAMES", "ALLOWED_MEDIAS", mode='before')
    def validate_fields(cls, v: str) -> List[str]:
        try:
            result = v.split(',')
        except ValueError as V:
            raise V
        return result


setting = Settings()
