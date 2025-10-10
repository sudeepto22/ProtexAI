import os
import time
import uuid

import paho.mqtt.client as mqtt

from common.config.mqtt_config import MQTTConfig
from common.utils.logger import setup_logger
from common.utils.mqtt_client import MQTTClient
from sensor.metrics import get_system_metrics

logger = setup_logger("Producer")
config = MQTTConfig()

INTERVAL = int(os.getenv("RUN_INTERVAL_SECONDS", 5))


def publish_messages(client: mqtt.Client, topic: str | None = None) -> None:
    if topic is None:
        topic = config.TOPIC

    try:
        while True:
            metrics = get_system_metrics()
            metrics_json = metrics.to_json()
            result = client.publish(topic, metrics_json, qos=config.QOS)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published: {metrics}")
            else:
                logger.error("Failed to publish message")

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        logger.info("Producer stopped by user")


def start_producer() -> None:
    # Generate unique client ID to allow multiple producer instances
    client_id = f"protexai-producer-{uuid.uuid4().hex[:8]}"
    logger.info(
        f"MQTT Broker: {config.BROKER_HOST}:{config.BROKER_PORT} Topic: {config.TOPIC} Client ID: {client_id}`"
    )

    try:
        with MQTTClient(client_id=client_id, logger=logger) as client:
            publish_messages(client)

    except KeyboardInterrupt:
        logger.info("Producer stopped by user")

    except Exception:
        logger.exception("ProducerError")


if __name__ == "__main__":
    start_producer()
