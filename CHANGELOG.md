# Changelog
## v0.1.3 (2025-10-21)

### Added
- Fully functional implementations of command-line interface (CLI) and API for log tracing.
- Support for local files, AWS S3, Google Cloud Storage, Kafka, and Datadog log sources via plugins.
- Configuration management with `pipetracker.yaml` and `config --init` command.
- Security features including PII masking and optional log encryption.
- Visualization support with CLI and HTML output using Plotly and NetworkX.
- Unit and integration tests in the `tests/` directory.

### Changed
- Refined plugin architecture for functionality, better extensibility, and maintainability.
- Optimized performance tracking with the `PerformanceTracker` class.

### Fixed
- First stable release.
- Resolved resource exhaustion constraint with configurable `max_files` and `max_size_mb` limits.

## v0.0.1 (2025-10-17)
### Added
- Initial project structure with modular design for core components and plugins.
- Basic trace functionality for local log files.
- Added lazy-loading for plugins (Kafka, S3, GCS, Datadog).
- Typer CLI entrypoint added.
- Unit tests added for all plugins.
- Documentation written (README + docs/*).
- Docker support added.

### Known Issues
- Unstabble.
- Limited plugin support; additional sources require custom implementation.
- No automated deployment configuration.
