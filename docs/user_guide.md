# User Guide

This guide provides detailed instructions for using Pipetracker, a tool for tracing logs across distributed microservice environments. It covers installation, configuration, usage examples, and troubleshooting, tailored for users ranging from developers to system administrators.

## Introduction

Pipetracker enables users to trace log entries by identifiers (e.g., `transaction_id`, `request_id`) across local files, AWS S3, Google Cloud Storage (GCS), Kafka, and Datadog. It offers a command-line interface (CLI) and a RESTful API, with features for security, visualization, and service verification.

## Installation

Follow these steps to install Pipetracker:

```bash
git clone https://github.com/dare-afolabi/pipetracker.git
cd pipetracker
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install .
pip install .[kafka,aws,gcs,datadog]
```

### Configure Credentials
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export KAFKA_SASL_USERNAME=your-username
export KAFKA_SASL_PASSWORD=your-password
export KAFKA_BOOTSTRAP=broker1:9092,broker2:9092  # Optional
export DD_API_KEY=your-api-key
export DD_APP_KEY=your-app-key
export DD_SITE=datadoghq.com  # Optional
export APP_SECRET_KEY=your-encryption-key
export SERVICE_NAME=pipetracker  # Optional
export DEBUG=false  # Optional
```

## Configuration

Generate a default configuration:
```bash
pipetracker config --init
```

### Example `pipetracker.yaml`
```yaml
log_sources:
  - ./logs
  - s3://my-bucket/logs/
match_keys:
  - transaction_id
output:
  format: html
  path: ./output
  max_files: 100
  max_size_mb: 10
verifier_endpoints:
  service_a: http://localhost:8000/verify
security:
  encrypt_logs: false
```

## CLI Usage

Trace a log:
```bash
pipetracker trace TXN12345 --config pipetracker.yaml
```

## API Usage

Start the API:
```bash
uvicorn pipetracker.api.main:app --host 0.0.0.0 --port 8000
```

Check health:
```bash
curl http://localhost:8000/health
```

Trace a log:
```bash
curl http://localhost:8000/trace/TXN12345?config_path=pipetracker.yaml
```

## Troubleshooting

- **No Logs Found**: Verify log source paths and credentials.  
- **Resource Limits Exceeded**: Adjust `max_files` or `max_size_mb`.  
- **Credential Errors**: Ensure environment variables or encrypted files are properly configured.  
- **API Unavailable**: Ensure the API server is running.

## Best Practices

- Use encrypted secrets for credentials.  
- Adjust performance limits based on data volume.  
- Regularly back up `output` and `pipetracker.yaml`.  
- Review `CHANGELOG.md` for updates.

*Generated on October 21, 2025*