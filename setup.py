from setuptools import setup, find_packages

setup(
    name="pipetracker",
    version="0.1.3",
    description="Data flow and lineage tracer for \
        distributed microservice logs",
    author="Dare Afolabi",
    author_email="dare.afolabi@outlook.com",
    url="https://github.com/dare-afolabi/pipetracker",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.19.2",
        "pandas>=2.2.2",
        "pydantic>=2.2.2",
        "pydantic-settings>=1.0.5",
        "fastapi>=0.95.0,<1.0.0",
        "uvicorn>=0.29.0",
        "networkx>=3.3",
        "matplotlib>=3.8",
        "plotly>=5.22.0",
        "requests>=2.32.3",
        "requests-mock>0.22.0",
        "PyYAML>=6.0.1",
        "cryptography>=42.0.8",
        "filelock>=3.15.4",
    ],
    extras_require={
        "kafka": ["confluent-kafka>=2.12.0", "six>=1.16.0"],
        "aws": ["boto3>=1.34.131"],
        "gcs": ["google-cloud-storage>=2.16.0"],
        "datadog": ["datadog-api-client>=2.19.0", "datadog>=0.44"],
        "dev": [
            "pytest>=8.2.2",
            "pytest-cov>=5.0.0",
            "pytest-mock>=3.10.0",
            "black>=24.4.2",
            "mypy>=1.10.1",
            "isort>=5.13.2",
            "coverage>=7.5.3",
            "moto>=5.0.4",
            "httpx>=0.28.1",
            "loguru>=0.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pipetracker = pipetracker.cli.main:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
