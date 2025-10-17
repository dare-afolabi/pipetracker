from pipetrack.plugins import kafka_plugin


def test_kafka_plugin_send(monkeypatch):
    class FakeProducer:
        def send(self, topic, value):
            return f"sent to {topic}"

    monkeypatch.setattr(
        kafka_plugin,
        "_get_kafka_producer",
        lambda: lambda **kw: FakeProducer(),
    )

    plugin = kafka_plugin.KafkaPlugin(brokers=["fake:9092"], topic="t")
    res = plugin.send({"msg": "hi"})
    assert res == "sent to t"
