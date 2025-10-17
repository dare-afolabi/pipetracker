![logo](assets/logo.jpeg)
 
<div align="center">
  <a href="https://github.com/dare-afolabi/pipetrack/releases">
    <img src="https://img.shields.io/github/v/tag/dare-afolabi/pipetrack" alt="🧩">
  </a>
  <a href="https://github.com/dare-afolabi/pipetrack?tab=MIT-1-ov-file#readme">
    <img src="https://img.shields.io/github/license/dare-afolabi/pipetrack" alt="📄">
  </a>
  <a href="https://github.com/sponsors/dare-afolabi">
    <img src="https://img.shields.io/github/sponsors/dare-afolabi" alt="🙏">
  </a>
  <a href="https://github.com/dare-afolabi/pipetrack/stargazers">
    <img src="https://img.shields.io/github/stars/dare-afolabi/pipetrack?style=flat" alt="⭐️">
  </a>
</div>

# Pipetrack
 
**Pipetrack** is a modular log ingestion and processing framework. It provides a lightweight CLI, plugin system, and integrations for streaming or batch log collection from multiple backends.

---

## Features
- Pluggable log sources (S3, GCS, Kafka, Datadog, local files)
- Typer-based CLI for simple commands
- Pydantic-based configuration (YAML + env overrides)
- Lazy-loaded SDKs (no heavy dependencies unless needed)
- CI/CD with pytest and coverage
- Docker-ready for deployment

---

## Installation

```bash
# From PyPI (once published)
pip install pipetrack

# From source
git clone https://github.com/dare-afolabi/pipetrack.git
cd pipetrack
pip install -e ".[dev]"

# Docker
docker pull dare-afolabi/pipetrack:latest
```

---

## Usage

### CLI

```bash
pipetrack --help
```

Examples:

```bash
# Scan logs from multiple sources
pipetrack scan --config config.yaml

# Send logs to Datadog
pipetrack send datadog --api-key $DD_API_KEY
```

### API

Start the FastAPI service:

```bash
uvicorn pipetrack.api.main:app --reload
```

---

## Configuration

Configuration is provided in **YAML** and validated with **Pydantic**.

```yaml
log_sources:
  - "s3://my-bucket/logs/"
  - "gs://my-logs-bucket/"
  - "kafka://localhost:9092/my-topic"
  - "datadog://"
match_keys:
  - "trace_id"
  - "span_id"
output:
  format: "json"
  path: "./output"
verifier_endpoints:
  health: "http://localhost:8000/health"
security:
  encrypt_logs: false
```

Env overrides supported via `.env` file:

```
KAFKA_BOOTSTRAP=localhost:9092
SERVICE_NAME=pipetrack
DEBUG=true
```

---

## Plugins

Available sources:

* **S3** (`pipetrack.plugins.s3_plugin.S3Plugin`)
* **GCS** (`pipetrack.plugins.gcs_plugin.GCSPlugin`)
* **Kafka** (`pipetrack.plugins.kafka_plugin.KafkaPlugin`)
* **Datadog** (`pipetrack.plugins.datadog_plugin.DatadogPlugin`)
* **Local filesystem** (`pipetrack.plugins.local_plugin.LocalPlugin`)

All plugins use **lazy imports** to avoid heavy dependencies unless explicitly used.

---

## Development

```bash
# Run tests
pytest --maxfail=1 --disable-warnings -q

# Run with coverage
pytest --cov=pipetrack tests/
```

---

## Docker

```bash
docker build -t pipetrack .
docker run -it pipetrack scan --config config.yaml
```

---

## License

MIT License © 2025 Dare Afolabi.
