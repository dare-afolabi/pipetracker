# Contributing to Pipetracker

Thank you for your interest in contributing to Pipetracker! This document outlines the process for contributing to the project, including setting up a development environment, submitting changes, and following coding standards.

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Dependencies: Install core and dev dependencies:
  ```bash
  git clone https://github.com/dare-afolabi/pipetracker.git
  cd pipetracker
  pip install .[dev,kafka,aws,gcs,datadog]
  ```

### Setting Up the Development Environment
1. **Fork and Clone:**
   ```bash
   git clone https://github.com/dare-afolabi/pipetracker.git
   cd pipetracker
   ```
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install .[dev,kafka,aws,gcs,datadog]
   ```
4. **Generate Configuration:**
   ```bash
   pipetracker config --init
   ```

See [docs/development.md](./docs/development.md) for detailed setup.

### Development Workflow

#### Code Style
- Follow PEP 8 guidelines.
- Use type hints for all functions and classes.
- Format code with black:
  ```bash
  black .
  ```
- Run type checks with mypy:
  ```bash
  mypy .
  ```

#### Testing
Run tests to ensure your changes don’t break existing functionality:
```bash
pytest tests/ --cov=pipetracker --cov-report=html
```

#### Adding a New Plugin
1. Create a new file in `pipetracker/plugins/` (e.g., `my_plugin.py`).
2. Extend the `LogSourcePlugin` class and implement `fetch_logs`.
3. Update `pipetracker.yaml` with your new source.
4. Add integration tests in `tests/integration/test_my_plugin.py`.

See `docs/plugins.md` for detailed plugin development instructions.

#### Submitting Changes
1. Create a Branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Commit Changes:
   ```bash
   git commit -m "Add MyPlugin for custom log source"
   ```
3. Run Tests:
   ```bash
   black .
   mypy .
   pytest tests/
   ```
4. Push and Create a Pull Request:
   ```bash
   git push origin feature/my-new-feature
   ```
5. Open a PR on GitHub.

#### Production Considerations
- Use environment variables or secret managers for credentials.
- Test new plugins with large datasets.
- Handle errors gracefully.
- Update docs and README with any new features.

## Continuous Integration

Pipetracker uses GitHub Actions for automated CI. Checks include linting, type checking, and testing. See [workflows/python-ci.yml](../workflows/python-ci.yml) for the workflow configuration. Ensure your changes pass CI before submitting a pull request.

*Generated on October 21, 2025*