import pytest
from pipetracker.plugins.kafka_plugin import KafkaPlugin
from unittest.mock import patch
import os


@pytest.fixture
def kafka_setup():
    # Patch the Consumer class inside the plugin itself
    with patch("pipetracker.plugins.kafka_plugin.Consumer") as MockConsumer:
        mock_consumer = MockConsumer.return_value
        mock_consumer.__iter__.return_value = [
            type("Message", (), {"value": b"transaction_id=123"})
        ]
        yield mock_consumer


def test_kafka_plugin_fetch_logs(kafka_setup, monkeypatch):
    """Test the KafkaPlugin's fetch_logs method to ensure it retrieves \
        and stores log messages from a Kafka topic."""
    # Mock environment variables for credentials
    monkeypatch.setenv("KAFKA_SASL_USERNAME", "fake_user")
    monkeypatch.setenv("KAFKA_SASL_PASSWORD", "fake_pass")

    # Initialize plugin
    plugin = KafkaPlugin()

    # Call the method under test
    log_files = plugin.fetch_logs(
        "kafka://localhost:9092/test-topic", max_files=10, max_size_mb=1.0
    )

    # Validate
    assert len(log_files) == 1
    assert os.path.exists(log_files[0])
    with open(log_files[0], "r", encoding="utf-8") as f:
        assert "transaction_id=123" in f.read()

    # Cleanup
    os.unlink(log_files[0])
