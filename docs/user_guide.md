# User Guide

## Installation

From PyPI (recommended):

```bash
pip install pipetrack
```

Or via Docker:

```bash
docker pull dare-afolabi/pipetrack:latest
```

Or from source:

```bash
git clone https://github.com/dare-afolabi/pipetrack.git
cd pipetrack
pip install -e .
```

## CLI Usage

See all commands:

```bash
pipetrack --help
```

### Scan logs

```bash
pipetrack scan --config config.yaml
```

### Send to Datadog

```bash
pipetrack send datadog --api-key $DD_API_KEY
```

## Config Files

Pipetrack uses a YAML config (`config.yaml`):

```yaml
log_sources:
  - "s3://my-logs/"
  - "gs://my-gcs-logs/"
  - "kafka://localhost:9092/my-topic"
match_keys:
  - "trace_id"
  - "span_id"
output:
  format: "json"
  path: "./output"
security:
  encrypt_logs: false
```

Environment variable overrides are supported through `.env`:

```env
KAFKA_BOOTSTRAP=localhost:9092
SERVICE_NAME=pipetrack
DEBUG=true
```

## API Usage

Start the FastAPI app:

```bash
uvicorn pipetrack.api.main:app --reload
```

Available endpoints:

* `GET /health` – health check
* `POST /logs` – submit logs

## Documentation

Minimal top-level structure:

```bash
pipetrack-main/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── docs/
│   ├── architecture.md
│   ├── developer_guide.md
│   └── user_guide.md
├── examples/
│   └── config.yaml
├── requirements-dev.txt
└── requirements.txt
```

See [`developer_guide.md`](./developer_guide.md) for the **full directory structure** and developer notes.
