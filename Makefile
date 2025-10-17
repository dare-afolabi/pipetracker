# pipetrack - Data Flow & Lineage Tracer

# Variables
APP_NAME = pipetrack
VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
UVICORN = $(VENV)/bin/uvicorn

# Default target
.DEFAULT_GOAL := help

# ENVIRONMENT SETUP

venv:  ## Create virtual environment and install dependencies
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip wheel
	@$(PIP) install -e .
	@$(PIP) install -r requirements-dev.txt
	@echo "Virtual environment ready."

clean:  ## Clean temporary files, caches, and build artifacts
	@rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache dist build *.egg-info
	@echo "Cleaned project."

# TESTING & LINTING

test:  ## Run all unit tests with pytest
	@$(PYTHON) -m pytest -q

lint:  ## Run linting using flake8 and black (if installed)
	@which flake8 >/dev/null 2>&1 && flake8 $(APP_NAME) || echo "flake8 not installed"
	@which black >/dev/null 2>&1 && black --check $(APP_NAME) || echo "black not installed"
	@echo "Lint check complete."

format:  ## Auto-format code using black
	@black $(APP_NAME)
	@echo "Code formatted."

# APPLICATION COMMANDS

run-cli:  ## Run CLI help (ensure entrypoint works)
	@$(PYTHON) -m $(APP_NAME).cli.main --help

trace:  ## Example CLI trace run (change ID as needed)
	@pipetrack trace TXN12345 --config pipetrack.yaml

api:  ## Run FastAPI server locally
	@$(UVICORN) $(APP_NAME).api.main:app --reload

# DOCKER COMMANDS

docker-build:  ## Build Docker image
	@docker build -t $(APP_NAME):latest .

docker-run:  ## Run Docker container on port 8000
	@docker run -p 8000:8000 $(APP_NAME):latest

docker-clean:  ## Remove dangling Docker images and containers
	@docker system prune -f
	@echo "Cleaned Docker artifacts."

# UTILITIES

install-dev:  ## Install dev dependencies
	@$(PIP) install -r requirements-dev.txt || echo "No dev requirements file."

help:  ## Show this help message
	@echo ""
	@echo "pipetrack - available make targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""