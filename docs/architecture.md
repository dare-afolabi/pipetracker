# Architecture

## High-Level Design
Pipetrack is organized into modular layers:

- **core/** – Configuration, log scanning, common utilities
- **cli/** – Typer-based command-line interface
- **api/** – FastAPI service for programmatic access
- **plugins/** – Log source integrations (S3, GCS, Kafka, Datadog, local)
- **integrations/** – Lower-level helpers (internal use, not public API)
- **tests/** – Unit + integration tests
- **docs/** – Documentation

## Directory Structure

```bash

pipetrack/
    api/
        main.py
    cli/
        main.py
    core/
        config_loader.py
        log_scanner.py
        plugin_loader.py
    plugins/
        kafka_plugin.py
        s3_plugin.py
        gcs_plugin.py
        datadog_plugin.py
        local_plugin.py
...

tests/
    unit/
    integration/
docs/
    architecture.md
    developer_guide.md
    user_guide.md

```

## Plugin System
- Plugins are Python classes implementing a uniform interface (`upload`, `send`, or `fetch_logs`).
- Loaded dynamically via `load_plugin(path)`.
- Heavy SDKs (boto3, google-cloud, datadog) are **lazy-loaded**.

## Config System
- YAML configs parsed with `yaml.safe_load`.
- Pydantic models validate schema.
- Env overrides via `.env`.

## CLI
- Built with Typer.
- Subcommands: `scan`, `send`, etc.
