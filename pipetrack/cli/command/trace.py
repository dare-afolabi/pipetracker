import os
import tempfile
import typer

from pipetrack.core.config_loader import ConfigLoader
from pipetrack.core.log_scanner import LogScanner
from pipetrack.core.pattern_matcher import PatternMatcher
from pipetrack.core.trace_builder import TraceBuilder
from pipetrack.core.visualizer import Visualizer
from pipetrack.core.verifier import Verifier
from pipetrack.core.security import Security
from pipetrack.core.performance import PerformanceTracker


def trace(
    id: str = typer.Argument(
        ..., help="Trace ID to match (e.g., transaction_id value)."
    ),
    config: str = typer.Option(
        "pipetrack.yaml", help="Path to configuration file."
    ),
):
    """
    Perform log tracing based on the provided ID.
    """
    tracker = PerformanceTracker()
    tracker.mark("start")

    try:
        conf = ConfigLoader().load(config)
    except Exception as e:
        typer.echo(f"Error loading config: {e}")
        raise typer.Exit(1)

    security = Security(conf.security.encrypt_logs)
    scanner = LogScanner(conf.log_sources)
    files = scanner.scan()

    matcher = PatternMatcher(conf.match_keys)
    matches = []

    for file_path in files:
        try:
            with open(file_path) as fh:
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
            typer.echo(f"Error processing {file_path}: {e}")
        finally:
            if file_path.startswith(tempfile.gettempdir()):
                try:
                    os.unlink(file_path)
                except Exception:
                    pass

    df = TraceBuilder().build(matches)
    visualizer = Visualizer()

    output_format = conf.output.format
    output_path = f"{conf.output.path}trace_{id}.{output_format}"
    os.makedirs(conf.output.path, exist_ok=True)

    if output_format == "html":
        visualizer.to_html(df, output_path)
        typer.echo(f"Trace output saved to {output_path}")
    else:
        typer.echo(visualizer.to_cli(df))

    verifier = Verifier()
    if not df.empty:
        for service in df["service"].unique():
            if service in conf.verifier_endpoints:
                result = verifier.verify(
                    service, id, conf.verifier_endpoints[service]
                )
                typer.echo(f"Verification for {service}: {result}")

    typer.echo(f"Duration: {tracker.duration('start'):.2f} seconds")
