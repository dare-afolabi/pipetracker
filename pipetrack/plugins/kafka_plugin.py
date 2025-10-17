from typing import Optional, Any
import json


def _get_kafka_producer() -> Optional[Any]:
    try:
        from kafka import KafkaProducer

        return KafkaProducer
    except ImportError:
        return None


class KafkaPlugin:
    def __init__(self, brokers: list[str], topic: str) -> None:
        KafkaProducer = _get_kafka_producer()
        if KafkaProducer is None:
            raise ImportError(
                "kafka-python is not installed. Cannot use KafkaPlugin."
            )

        self.producer = KafkaProducer(
            bootstrap_servers=brokers,
            value_serializer=lambda v: json.dumps(v).encode(
                "utf-8"
            ),  # serialize dicts
        )
        self.topic = topic

    def send(self, message: dict) -> Any:
        """Send a dictionary message to Kafka."""
        return self.producer.send(self.topic, value=message)
