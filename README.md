![logo](assets/logo.jpeg)
 
<div align="center">
  <a href="https://github.com/dare-afolabi/pipetracker/releases">
    <img src="https://img.shields.io/github/v/tag/dare-afolabi/pipetracker" alt="Tag">
  </a>
  <a href="https://github.com/dare-afolabi/pipetracker?tab=MIT-1-ov-file#readme">
    <img src="https://img.shields.io/github/license/dare-afolabi/pipetracker" alt="License">
  </a>
  <a href="https://github.com/sponsors/dare-afolabi">
    <img src="https://img.shields.io/github/sponsors/dare-afolabi" alt="Sponsors">
  </a>
  <a href="https://github.com/dare-afolabi/pipetracker/stargazers">
    <img src="https://img.shields.io/github/stars/dare-afolabi/pipetracker?style=flat" alt="Stars">
  </a>
</div>

# Pipetracker

Pipetracker is a Python-based tool for tracing logs across distributed microservice environments. It supports log retrieval from local files, AWS S3, Google Cloud Storage (GCS), Kafka, and Datadog, with an extensible plugin architecture for additional sources. Pipetracker provides a command-line interface (CLI) and a REST API to trace logs by identifiers (e.g., transaction IDs), with features for PII masking, log encryption, visualization, service verification, and performance tracking.

## Features

- **Distributed Log Tracing**: Trace identifiers across logs from local files, S3, GCS, Kafka, and Datadog.
- **Plugin Architecture**: Extensible plugins for integrating new log sources.
- **Security**: PII masking, log encryption, and secure credential management for plugins.
- **Scalability**: Configurable limits (`max_files`, `max_size_mb`) to prevent resource exhaustion.
- **Visualization**: Outputs traces in CLI or HTML format (using Plotly and NetworkX for graphs).
- **CLI and API**: User-friendly CLI with Typer and FastAPI-based REST API.
- **Verification**: Validate traces against service endpoints.
- **Performance Tracking**: Measure and report trace operation durations.

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/dare-afolabi/pipetracker.git
cd pipetracker
```

### 2. Install Dependencies
```bash
pip install .
```

### 3. Install Plugin Extras
```bash
pip install .[kafka,aws,gcs,datadog]
```

### 4. Generate Configuration
```bash
pipetracker config --init
```

### 5. Run a Trace
```bash
pipetracker trace TXN12345 --config pipetracker.yaml
```

## Documentation
Detailed documentation is available in the `docs/` directory:

- [User Guide](./docs/user_guide.md)
- [Installation](./docs/installation.md)
- [Usage](./docs/usage.md)
- [Plugins](./docs/plugins.md)
- [Development](./docs/development.md)
- [Deployment](./docs/deployment.md )
- [Architecture](./docs/architecture.md)

## Contributing
Contributions are welcome! See [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for setup and submission guidelines.

## License
MIT License. See [LICENSE](./LICENSE) for details.

---

*Generated on October 21, 2025*
