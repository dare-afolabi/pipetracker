# Contributing to Pipetrack

## Getting Started
Thank you for contributing to **Pipetrack**! This project welcomes contributions from the community.

## Environment Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/dare-afolabi/pipetrack.git
   cd pipetrack
   ```
2. Set up a virtual environment:
   ```bash
   make venv
   ```
3. Copy `.env.example` to `.env` and populate with credentials (e.g., AWS, GCS, Kafka, Datadog). Do not commit secrets.

## Development Guidelines
- **Code Style**: Follow PEP8, use Black for formatting, and Flake8 for linting.
- **Type Hints**: Use type annotations and ensure mypy compliance.
- **Testing**: Add tests for new features under `tests/`. Run make test to verify.
- **Commits**: Use clear, descriptive commit messages.
- **Pull Requests**: Open an issue first for significant changes. Ensure tests pass and code is linted.

## Submitting Changes
1. Fork the repository and create a feature branch.
2. Run make format and make lint before committing.
3. Run make test to ensure tests pass.
4. Submit a pull request with a clear description.

## Code of Conduct
Follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions.
