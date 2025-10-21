.PHONY: install test lint format run clean

install:
	pip install --no-cache-dir -e .[dev,kafka,aws,gcs,datadog]

test:
	pytest tests/ --cov=pipetracker --cov-report=html

lint:
	black .
	mypy .

format:
	black .
	isort .

run:
	uvicorn pipetracker.api.main:app --host 0.0.0.0 --port 8000

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.pyc" -exec rm -r {} +
	rm -rf .coverage htmlcov output/*

config:
	pipetracker config --init