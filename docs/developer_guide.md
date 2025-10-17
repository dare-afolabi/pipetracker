# Developer Guide

## Setup
```bash
git clone https://github.com/dare-afolabi/pipetrack.git
cd pipetrack
pip install -e ".[dev]"
````

## Running Tests

```bash
pytest
pytest --cov=pipetrack
```

Tests are organized under:

* `tests/unit/`
* `tests/integration/`

## Linting

```bash
flake8 pipetrack
black pipetrack
```

## GitHub Actions

CI runs on every push:

* Install deps
* Lint
* Run pytest + coverage

Config: `.github/workflows/ci.yml`

## Full Directory Stucture

```bash
pipetrack-main/
├── CHANGELOG.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── assets/
│   └── logo.jpeg
├── docker-compose.yml
├── docs/
│   ├── CODE_OF_CONDUCT.md
│   ├── CONTRIBUTING.md
│   ├── architecture.md
│   ├── developer_guide.md
│   └── user_guide.md
├── examples/
│   └── config.yaml
├── logging.conf
├── pipetrack/
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── trace.py
│   ├── cli/
│   │   ├── main.py
│   │   └── command/
│   │       ├── __init__.py
│   │       ├── config.py
│   │       └── trace.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   ├── log_scanner.py
│   │   ├── pattern_matcher.py
│   │   ├── performance.py
│   │   ├── plugin_loader.py
│   │   ├── security.py
│   │   ├── trace_builder.py
│   │   ├── utils.py
│   │   ├── verifier.py
│   │   └── visualizer.py
│   └── plugins/
│       ├── __init__.py
│       ├── base.py
│       ├── datadog_plugin.py
│       ├── gcs_plugin.py
│       ├── kafka_plugin.py
│       ├── loader.py
│       ├── local_plugin.py
│       └── s3_plugin.py
├── pipetrack.yaml
├── pyproject.toml
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
├── setup.cfg
├── setup.py
└── tests/
    ├── __init__.py
    ├── integration/
    │   ├── __init__.py
    │   └── test_full_trace.py
    ├── mocks/
    │   └── __init__.py
    ├── test_api.py
    ├── test_cli.py
    ├── test_core.py
    └── unit/
        ├── __init__.py
        ├── test_cli_commands.py
        ├── test_config_loader.py
        ├── test_datadog_plugin.py
        ├── test_gcs_plugin.py
        ├── test_kafka_plugin.py
        ├── test_loader.py
        ├── test_local_plugin.py
        ├── test_log_scanner.py
        ├── test_s3_plugin.py
        ├── test_trace_builder.py
        ├── test_verifier.py
        └── test_visualizer.py

```

## Contributing

* Fork + PR workflow
* Write unit tests for new plugins
* Update docs for any new features
