"""Application configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    api_secret_key: str = "change-this-to-a-secure-random-key"

    # Database
    database_url: str = "postgresql+asyncpg://quant:quant_pass@localhost:5432/al_syaka_quant"

    # Redis & Celery
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Market Data Providers
    yahoo_finance_enabled: bool = True
    polygon_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    massive_api_key: Optional[str] = None

    # MT5
    mt5_account: Optional[int] = None
    mt5_password: Optional[str] = None
    mt5_server: Optional[str] = None

    # Logging
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("mt5_account", mode="before")
    @classmethod
    def parse_mt5_account(cls, v):
        if v == "" or v is None:
            return None
        return int(v)


settings = Settings()
