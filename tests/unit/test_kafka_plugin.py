from pipetracker.plugins import kafka_plugin


class TestKafkaPlugin(kafka_plugin.KafkaPlugin):
    def __init__(self, brokers=None, topic=None):
        super().__init__()
        self.brokers = brokers
        self.topic = topic

    def fetch_logs(self, source, max_files=100, max_size_mb=10.0):
        return []


def test_kafka_plugin_send(monkeypatch):
    """Test the send method of KafkaPlugin using a mocked Kafka \
        producer."""

    class FakeProducer:
        def __init__(self):
            self.sent = []

        def send(self, topic, value):
            self.sent.append((topic, value))

        def flush(self):
            pass

    monkeypatch.setattr(
        TestKafkaPlugin, "_get_producer", lambda self, **kwargs: FakeProducer()
    )
    monkeypatch.setenv("KAFKA_SASL_USERNAME", "fake_user")
    monkeypatch.setenv("KAFKA_SASL_PASSWORD", "fake_pass")
    plugin = TestKafkaPlugin(brokers=["fake:9092"], topic="t")
    plugin.send("some-topic", b'{"key": "value"}')
    assert plugin.producer.sent[0] == ("some-topic", b'{"key": "value"}')


def test_kafka_plugin_integration(monkeypatch):
    """Test the integration of KafkaPlugin's send method with a mocked \
        Kafka producer."""

    class FakeProducer:
        def __init__(self, **kwargs):
            self.sent = []

        def send(self, topic, **kwargs):
            self.sent.append((topic, kwargs.get("value")))

        def flush(self):
            pass

    monkeypatch.setattr(
        TestKafkaPlugin, "_get_producer", lambda self, **kwargs: FakeProducer()
    )
    monkeypatch.setenv("KAFKA_SASL_USERNAME", "fake_user")
    monkeypatch.setenv("KAFKA_SASL_PASSWORD", "fake_pass")
    plugin = TestKafkaPlugin()
    plugin.send("topic1", b"msg")
    assert plugin.producer.sent[0] == ("topic1", b"msg")
