# Plugins

Pipetracker supports an extensible plugin architecture for different log sources.

## Built-In Plugins

### LocalPlugin
Reads logs from local directories.

### S3Plugin
Fetches logs from S3 buckets.  
Env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`.

### GCSPlugin
Fetches logs from Google Cloud Storage.  
Env var: `GOOGLE_APPLICATION_CREDENTIALS`.

### KafkaPlugin
Consumes messages from Kafka topics.  
Env vars: `KAFKA_SASL_USERNAME`, `KAFKA_SASL_PASSWORD`.

### DatadogPlugin
Queries logs from Datadog.  
Env vars: `DD_API_KEY`, `DD_APP_KEY`.

## Developing Custom Plugins
1. Create a plugin in `pipetracker/plugins/`.
2. Extend `LogSourcePlugin`.
3. Implement `fetch_logs()`.
4. Add tests and update documentation.

*Generated on October 21, 2025*