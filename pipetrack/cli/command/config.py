import typer
from pipetrack.core.config_loader import ConfigLoader
from pydantic import BaseModel, ValidationError
from typing import Any  # For flexibility in args handling


def config(
    path: str = typer.Option(
        "pipetrack.yaml", help="Path to configuration file."
    )
):
    """
    Load and display the configuration for validation.
    """
    try:
        conf = ConfigLoader().load(path)
        typer.echo(conf.dict())
    except ValidationError as e:
        typer.echo(f"Validation error in config: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error loading config: {e}")
        raise typer.Exit(code=1)


class CLIConfig(BaseModel):
    input: str
    output: str
    log_level: str = "INFO"  # Could be extended to str | None if nullable


def load_cli_config(args: Any) -> CLIConfig:
    try:
        cfg = CLIConfig(**vars(args))
    except ValidationError as e:
        typer.echo(
            f"Invalid CLI config: {e}", err=True
        )  # Use Typer for consistent output
        raise typer.Exit(code=2)
    return cfg
