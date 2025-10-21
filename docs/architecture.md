# Architecture

This document provides an overview of the architectural design of Pipetracker, a Python-based tool for tracing logs across distributed microservice environments. It outlines the system's components, their interactions, and the principles guiding its scalability, security, and extensibility.

## Overview

Pipetracker is designed as a modular, plugin-based system to retrieve, process, and visualize log traces from various sources. The architecture separates concerns into distinct layers: configuration management, log retrieval, processing, visualization, and API/CLI interfaces. This modularity enables easy extension through plugins and supports deployment in diverse environments.

## High-Level Architecture

### Components

1. **Configuration Layer**
   - **Description**: Manages the configuration file (`pipetracker.yaml`) and environment variables.
   - **Implementation**: The `ConfigLoader` class in `pipetracker/core/config_loader.py` parses and validates configuration settings (e.g., `log_sources`, `match_keys`, `max_files`, `max_size_mb`).
   - **Interaction**: Provides settings to all other components, ensuring consistent behavior across the system.

2. **Log Retrieval Layer**
   - **Description**: Handles data ingestion from multiple log sources via plugins.
   - **Implementation**: The `LogSourcePlugin` base class in `pipetracker/plugins/base.py` defines the `fetch_logs` interface. Specific plugins (e.g., `S3Plugin`, `KafkaPlugin`) extend this class to fetch logs from AWS S3, Google Cloud Storage, Kafka, Datadog, and local files.
   - **Features**: Downloads remote logs to temporary files, respects `max_files` and `max_size_mb` limits, and uses the `Security` class for credential management.
   - **Scalability**: Employs pagination (S3, GCS, Datadog) and timeouts (Kafka) to handle large datasets efficiently.

3. **Processing Layer**
   - **Description**: Analyzes retrieved logs to identify traces based on match keys (e.g., `transaction_id`, `request_id`).
   - **Implementation**: The `TraceProcessor` class in `pipetracker/core/processor.py` processes log lines, applies PII masking via the `Security` class, and optionally encrypts output if `encrypt_logs` is enabled.
   - **Performance**: The `PerformanceTracker` class logs operation durations to monitor efficiency.

4. **Visualization Layer**
   - **Description**: Generates human-readable outputs in CLI or HTML format.
   - **Implementation**: The `Visualizer` class in `pipetracker/core/visualizer.py` uses `pandas` for data structuring, `NetworkX` for trace graphs, and `Plotly` for interactive HTML output.
   - **Output**: Saves results to the `output` directory, respecting the configured `format` (CLI or HTML).

5. **Interface Layer**
   - **Description**: Provides user access through CLI and RESTful API.
   - **Implementation**:
     - **CLI**: Built with `Typer` in `pipetracker/cli/main.py`, offering `trace` and `config` commands.
     - **API**: Implemented with `FastAPI` in `pipetracker/api/main.py`, exposing `/health` and `/trace/{trace_id}` endpoints.
   - **Interaction**: The CLI and API delegate to the `TraceProcessor` and `Visualizer` for core functionality.

6. **Security Layer**
   - **Description**: Ensures secure handling of credentials and sensitive data.
   - **Implementation**: The `Security` class in `pipetracker/core/security.py` manages encrypted secrets (e.g., `.datadog_api_key_secret`), masks PII (e.g., emails, long numbers), and supports log encryption with `APP_SECRET_KEY`.

### Data Flow

1. **Configuration Loading**: The application reads `pipetracker.yaml` and environment variables via `ConfigLoader`.
2. **Log Retrieval**: Plugins fetch logs based on configured `log_sources`, downloading to temporary files as needed.
3. **Processing**: `TraceProcessor` analyzes logs for match keys, applying security measures.
4. **Visualization**: `Visualizer` formats the trace data for output.
5. **Output Delivery**: Results are displayed via CLI or saved as HTML files, with verification against `verifier_endpoints` if configured.

### Diagram

[User] → [CLI/API Interface]  
↓  
[Config Loader] → [Log Retrieval Plugins]  
↓  
[Trace Processor] ← [Security]  
↓  
[Visualizer] → [Output Files]

## Design Principles

- **Modularity**: Plugins isolate log source logic, allowing easy addition of new sources (e.g., custom databases).  
- **Scalability**: Configurable limits (`max_files`, `max_size_mb`) and pagination prevent resource exhaustion.  
- **Security**: Centralized credential management and PII masking protect sensitive data.  
- **Extensibility**: The plugin architecture supports future enhancements without core code changes.  
- **Maintainability**: Clear separation of concerns and comprehensive logging facilitate debugging and updates.

## Deployment Architecture

- **CLI Deployment**: Runs as a standalone process, suitable for scheduled tasks (e.g., cron jobs).  
- **API Deployment**: Hosted with `uvicorn` behind a reverse proxy (e.g., Nginx) for scalability, secured with HTTPS and API key authentication.  
- **Containerization**: The provided `Dockerfile` supports deployment in containerized environments (e.g., Kubernetes), ensuring consistent runtime behavior.

## Performance Considerations

- **Resource Usage**: Temporary files are deleted post-processing to manage disk space.  
- **Parallel Processing**: Future enhancements could introduce multi-threading for plugin retrieval, pending optimization of `PerformanceTracker` metrics.  
- **Caching**: Log data is not cached; each trace operation fetches fresh data to ensure accuracy.

## Future Enhancements

- **Real-Time Tracing**: Integrate WebSocket support in the API for live log monitoring.  
- **Distributed Processing**: Add support for distributed tracing across multiple Pipetracker instances.  
- **Advanced Visualization**: Incorporate 3D graphs or heatmaps for complex trace analysis.

*Generated on October 21, 2025*
