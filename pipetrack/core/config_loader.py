import os
import yaml
from typing import List, Dict
from pydantic_settings import BaseSettings
from pydantic import BaseModel


# Then use normally:
class Settings(BaseSettings):
    kafka_bootstrap: str = "localhost:9092"
    debug: bool = False
    service_name: str = "pipetrack"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


class OutputConfig(BaseModel):
    format: str
    path: str


class SecurityConfig(BaseModel):
    encrypt_logs: bool


class Config(BaseModel):
    log_sources: List[str]
    match_keys: List[str]
    output: OutputConfig
    verifier_endpoints: Dict[str, str]
    security: SecurityConfig


class ConfigLoader:
    """Load and validate configuration from a YAML file."""

    def load(self, path: str) -> Config:
        """
        Load configuration and validate against the Pydantic schema.

        Args:
            path (str): Path to the YAML configuration file.
        Returns:
            Config: Validated configuration object.
        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If schema validation fails.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        try:
            return Config(**data)
        except Exception as e:
            raise ValueError(f"Invalid configuration format: {e}")
