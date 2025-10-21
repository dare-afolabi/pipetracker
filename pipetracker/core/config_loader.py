import os
import yaml
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import BaseModel


class Settings(BaseSettings):
    """Environment-level settings loaded from .env or environment variables."""

    kafka_bootstrap: str = "localhost:9092"
    debug: bool = False
    service_name: str = "pipetracker"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


class OutputConfig(BaseModel):
    format: str
    path: str
    max_files: int = 100
    max_size_mb: float = 10.0


class SecurityConfig(BaseModel):
    encrypt_logs: bool


class Config(BaseModel):
    """Structured YAML configuration schema."""

    log_sources: List[str]
    match_keys: List[str]
    output: OutputConfig
    verifier_endpoints: Dict[str, str]
    security: SecurityConfig


class ConfigLoader:
    """Load and validate configuration from a YAML file."""

    def load(self, path: str) -> Config:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise FileNotFoundError(f"Cannot read config {path}: {e}")
        try:
            return Config(**data)
        except Exception as e:
            raise ValueError(f"Invalid config format: {e}")
