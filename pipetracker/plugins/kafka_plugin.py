from pipetracker.plugins.base import LogSourcePlugin
from pipetracker.core.security import Security
import tempfile
import logging
from urllib.parse import urlparse
from typing import Optional, List, Any
import os
from confluent_kafka import Producer, Consumer

logger = logging.getLogger(__name__)


class KafkaPlugin(LogSourcePlugin):
    """Kafka plugin for fetching logs from topics."""

    def __init__(self, security: Optional[Security] = None) -> None:
        """Initialize the KafkaPlugin with an optional security instance.

        Args:
            security (Optional[Security]): Security instance for\
                 credential management.
        """
        self.producer: Optional[Producer] = None
        self.security = security or Security()

    def _get_producer(self, **kwargs: Any) -> Producer:
        """Lazily initialize and return a Producer instance.

        Args:
            **kwargs: Additional keyword arguments for Producer.

        Returns:
            Producer: Configured Kafka producer instance.

        Raises:
            ValueError: If Kafka credentials are not available.
        """
        from kafka import Producer

        kwargs.setdefault(
            "sasl_plain_username",
            self.security.get_plugin_secret(
                "kafka_username", env_var="KAFKA_SASL_USERNAME"
            ),
        )
        kwargs.setdefault(
            "sasl_plain_password",
            self.security.get_plugin_secret(
                "kafka_password", env_var="KAFKA_SASL_PASSWORD"
            ),
        )
        if not kwargs.get("sasl_plain_username") or not kwargs.get(
            "sasl_plain_password"
        ):
            raise ValueError("Kafka username and password are required.")
        return Producer(
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
            **kwargs,
        )

    def send(self, topic: str, message: bytes, **kwargs: Any) -> None:
        """Send a message to a Kafka topic.

        Args:
            topic (str): The Kafka topic to send to.
            message (bytes): The message data.
            **kwargs: Additional keyword arguments for the producer.
        """
        if self.producer is None:
            self.producer = self._get_producer(**kwargs)
        if self.producer is not None:  # Type safety check
            self.producer.send(topic, value=message)
            self.producer.flush()

    def fetch_logs(
        self, source: str, max_files: int = 100, max_size_mb: float = 10.0
    ) -> List[str]:
        """Fetch log messages from a Kafka topic.

        Args:
            source (str): Kafka URL (e.g., 'kafka://broker1,broker2/topic').
            max_files (int): Maximum number of files to process (default: 100).
            max_size_mb (float): Maximum total log size in MB (default: 10.0).

        Returns:
            List[str]: List of temporary file paths containing fetched logs.

        Raises:
            ValueError: If the source is not a valid Kafka URL.
            Exception: If an error occurs during Kafka operations.
        """
        if not source.startswith("kafka://"):
            raise ValueError(f"Invalid Kafka source: {source}")
        parsed = urlparse(source)
        brokers = parsed.netloc.split(",")
        topic = parsed.path.lstrip("/")
        consumer = Consumer(
            topic,
            bootstrap_servers=brokers,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            consumer_timeout_ms=10000,
            sasl_plain_username=self.security.get_plugin_secret(
                "kafka_username", env_var="KAFKA_SASL_USERNAME"
            ),
            sasl_plain_password=self.security.get_plugin_secret(
                "kafka_password", env_var="KAFKA_SASL_PASSWORD"
            ),
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
        )
        try:
            temp_path = tempfile.NamedTemporaryFile(delete=False).name
            total_size_bytes: int = 0
            max_size_bytes: int = int(max_size_mb * 1024 * 1024)
            with open(temp_path, "w", encoding="utf-8") as f:
                for msg in consumer:
                    line = msg.value.decode("utf-8", errors="ignore")
                    line_size = len(line.encode())
                    if total_size_bytes + line_size > max_size_bytes:
                        logger.info(
                            f"Reached max_size limit ({max_size_mb} MB)"
                        )
                        break
                    f.write(line + "\n")
                    total_size_bytes += line_size
            consumer.close()
            logger.info(f"Fetched Kafka logs from {topic} to {temp_path}")
            return [temp_path] if os.path.getsize(temp_path) > 0 else []
        except Exception as e:
            logger.error(f"Error fetching Kafka logs from {source}: {e}")
            raise
