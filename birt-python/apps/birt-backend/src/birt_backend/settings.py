from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="birt_", env_file=".env")

    log_level: Literal["CRITICAL", "FATAL", "ERROR", "WARN", "INFO", "DEBUG"] = "INFO"
