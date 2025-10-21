import os
import tempfile
import typer
import logging
from pipetracker.core.config_loader import ConfigLoader
from pipetracker.core.log_scanner import LogScanner
from pipetracker.core.pattern_matcher import PatternMatcher
from pipetracker.core.trace_builder import TraceBuilder
from pipetracker.core.visualizer import Visualizer
from pipetracker.core.verifier import Verifier
from pipetracker.core.security import Security
from pipetracker.core.performance import PerformanceTracker

app = typer.Typer(name="trace")
logger = logging.getLogger(__name__)


@app.command()
def trace(
    id: str = typer.Argument(
        ..., help="Trace ID to match (e.g., transaction_id value)."
    ),
    config: str = typer.Option(
        "pipetracker.yaml", help="Path to configuration file."
    ),
) -> None:
    """
    Perform log tracing based on the provided ID.

    Args:
        id: The trace ID to match (e.g., transaction_id value).
        config: Path to the configuration file (defaults to \
            'pipetracker.yaml').

    Returns:
        None: This function does not return a value; it performs side \
            effects such as
            printing to the console, writing to files, or raising exceptions.
    """
    tracker = PerformanceTracker()
    tracker.mark("start")

    # Load configuration
    try:
        conf = ConfigLoader().load(config)
    except Exception as e:
        logger.exception("Failed to load config")
        typer.echo(f"[ERROR] Loading config: {e}")
        raise typer.Exit(1)

    security = Security(conf.security.encrypt_logs)
    scanner = LogScanner(conf.log_sources, config=conf)

    # Scan for log files, handle empty sources gracefully
    try:
        files = scanner.scan()
    except ValueError as e:
        logger.warning(e)
        files = []

    matcher = PatternMatcher(conf.match_keys)
    matches = []

    # Process each log file
    for file_path in files:
        try:
            with open(file_path, encoding="utf-8") as fh:
                for line in fh:
                    decrypted = security.decrypt_log(line)
                    processed_line = security.mask_pii(decrypted)
                    if matcher.match_line(processed_line, id):
                        matches.append(
                            {
                                "timestamp": matcher.extract_timestamp(
                                    processed_line
                                ),
                                "service": matcher.extract_service(
                                    processed_line
                                ),
                                "raw": processed_line.strip(),
                            }
                        )
        except Exception as e:
            typer.echo(f"[WARNING] Error processing {file_path}: {e}")
        finally:
            # Clean up temp files
            if file_path.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(file_path)
                    logger.info(f"Deleted temporary file: {file_path}")
                except (PermissionError, OSError) as e:
                    logger.warning(
                        f"Failed to delete temporary file {file_path}: {e}"
                    )

    # Handle no matches
    if not matches:
        typer.echo("[INFO] No matches found.")
        raise typer.Exit(0)

    # Build trace DataFrame
    df = TraceBuilder().build(matches)
    visualizer = Visualizer()

    # Determine output path and format
    output_format: str = getattr(conf.output, "format", "cli")
    output_path: str = os.path.join(
        getattr(conf.output, "path", "./output"), f"trace_{id}.{output_format}"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Generate output
    if output_format.lower() == "html":
        visualizer.to_html(df, output_path)
        typer.echo(f"[INFO] Trace output saved to {output_path}")
    else:
        typer.echo(visualizer.to_cli(df))

    # Verify services
    verifier = Verifier()
    for service in df["service"].unique():
        if service in getattr(conf, "verifier_endpoints", {}):
            result = verifier.verify(
                service, id, conf.verifier_endpoints[service]
            )
            typer.echo(f"[INFO] Verification for {service}: {result}")

    # Print duration
    typer.echo(f"[INFO] Duration: {tracker.duration('start'):.2f} seconds")
