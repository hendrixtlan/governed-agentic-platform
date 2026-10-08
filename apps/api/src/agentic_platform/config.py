from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_mode: Literal["mock", "bedrock"] = "mock"
    aws_region: str = "us-east-1"
    bedrock_model_id: str = ""
    database_url: str | None = None
    enterprise_tools_url: str = "http://localhost:8100"
    max_sql_rows: int = 50
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
