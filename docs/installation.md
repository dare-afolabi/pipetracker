# Installation

This guide provides detailed instructions for installing Pipetracker.

## Prerequisites

- **Python**: Version 3.9+
- **Git**: For cloning the repository.
- **Dependencies**:
  - Core: `typer`, `pandas`, `fastapi`, `uvicorn`, `networkx`, `plotly`, `requests`, `PyYAML`, `cryptography`, `filelock`
  - Plugins:
    - AWS S3: `boto3`
    - GCS: `google-cloud-storage`
    - Kafka: `kafka-python`
    - Datadog: `datadog-api-client`
  - Dev: `pytest`, `black`, `mypy`, `moto`

## Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/dare-afolabi/pipetracker.git
   cd pipetracker
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install .[kafka,aws,gcs,datadog]
   ```
4. Verify installation:
   ```bash
   pipetracker --help
   ```

*Generated on October 21, 2025*