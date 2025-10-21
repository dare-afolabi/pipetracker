# Usage

This guide explains how to use Pipetracker’s CLI and API.

## Configuration

Generate default configuration:
```bash
pipetracker config --init
```

### Example `pipetracker.yaml`
```yaml
log_sources:
  - ./logs
  - s3://my-bucket/logs/
  - kafka://localhost:9092/topic
match_keys:
  - transaction_id
output:
  format: html
  path: ./output
  max_files: 100
  max_size_mb: 10
security:
  encrypt_logs: false
```

## CLI Usage

Trace a transaction:
```bash
pipetracker trace TXN12345 --config pipetracker.yaml
```

Generate configuration:
```bash
pipetracker config --init
```

## API Usage

Start the API:
```bash
uvicorn pipetracker.api.main:app --host 0.0.0.0 --port 8000
```

Health check:
```bash
curl http://localhost:8000/health
```

Trace endpoint:
```bash
curl http://localhost:8000/trace/TXN12345?config_path=pipetracker.yaml
```

*Generated on October 21, 2025*