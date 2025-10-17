from setuptools import setup, find_packages

setup(
    name="pipetrack",
    version="1.0.0",
    description="Data flow and lineage tracer for"
    "distributed microservice logs",
    author="Dare Afolabi",
    author_email="dare.afolabi@outlook.com",
    url="https://github.com/dare-afolabi/pipetrack",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.12",
        "pandas>=2.0",
        "pydantic>=2.0",
        "fastapi>=0.115",
        "uvicorn>=0.23",
        "networkx>=3.0",
        "matplotlib>=3.8",
        "plotly>=5.15",
        "requests>=2.31",
        "PyYAML>=6.0",
        "cryptography>=42.0.0",
    ],
    extras_require={
        "kafka": ["kafka-python>=2.0.2"],
        "aws": ["boto3>=1.26"],
        "gcs": ["google-cloud-storage>=2.9"],
        "datadog": ["datadog-api-client>=2.0.0", "datadog>=0.44"],
        "dev": ["pytest", "black", "mypy", "coverage"],
    },
    entry_points={
        "console_scripts": [
            "pipetrack = pipetrack.cli.main:app",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
