import typer
import logging
from pipetracker.core.config_loader import ConfigLoader
from pydantic import BaseModel, ValidationError
from typing import Any
import yaml

logger = logging.getLogger(__name__)


def config(
    path: str = typer.Option(
        "pipetracker.yaml", help="Path to configuration file."
    ),
    init: bool = typer.Option(
        False, "--init", help="Generate a default configuration file."
    ),
) -> None:
    """
    Load and display the configuration for validation, \
        or generate a default config.
    """
    if init:
        default_config = {
            "log_sources": ["./logs"],
            "match_keys": ["transaction_id"],
            "output": {
                "format": "html",
                "path": "./output",
                "max_files": 100,
                "max_size_mb": 10.0,
            },
            "verifier_endpoints": {},
            "security": {"encrypt_logs": False},
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump(default_config, f, default_flow_style=False)
            typer.echo(f"Generated default configuration at {path}")
        except Exception as e:
            logger.exception(f"Failed to generate config at {path}")
            typer.echo(f"[ERROR] Failed to generate config: {e}")
            raise typer.Exit(1)
        return

    try:
        conf = ConfigLoader().load(path)
        logger.info(f"Config loaded: {conf}")
        typer.echo(f"Configuration loaded successfully:\n{conf}")
    except Exception as e:
        logger.exception("Failed to load config")
        typer.echo(f"[ERROR] Loading config: {e}")
        raise typer.Exit(1)


class CLIConfig(BaseModel):
    input: str
    output: str
    log_level: str = "INFO"


def load_cli_config(args: Any) -> CLIConfig:
    try:
        cfg = CLIConfig(**vars(args))
    except ValidationError as e:
        typer.echo(f"Invalid CLI config: {e}", err=True)
        raise typer.Exit(code=2)
    return cfg
