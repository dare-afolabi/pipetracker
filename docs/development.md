# Development

Setup and testing instructions.

## Environment Setup
```bash
git clone https://github.com/dare-afolabi/pipetracker.git
cd pipetracker
python -m venv venv
source venv/bin/activate
pip install .[dev,kafka,aws,gcs,datadog]
pipetracker config --init
```

## Code Style
```bash
black .
mypy .
```

## Tests
```bash
pytest tests/ --cov=pipetracker --cov-report=html
```

**Unit tests**: `tests/unit/`  
**Integration tests**: `tests/integration/`

*Generated on October 21, 2025*