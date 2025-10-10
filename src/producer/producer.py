import time
import uuid

import paho.mqtt.client as mqtt

from common.config.mqtt_config import MQTTConfig
from common.utils.logger import setup_logger
from common.utils.mqtt_client import MQTTClient
from sensor.metrics import get_system_metrics

logger = setup_logger("Producer")
config = MQTTConfig()


def publish_messages(
    client: mqtt.Client, topic: str | None = None, interval: int = 5
) -> None:
    if topic is None:
        topic = config.TOPIC

    try:
        while True:
            metrics = get_system_metrics()
            metrics_json = metrics.to_json()
            result = client.publish(topic, metrics_json, qos=config.QOS)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                gpu_info = (
                    f", GPU={metrics.gpu[0].load_percent}%"
                    if metrics.gpu
                    else ", GPU=N/A"
                )
                temp_info = (
                    f", Temp={metrics.temperature[0].current_c}°C"
                    if metrics.temperature
                    else ", Temp=N/A"
                )
                cores_info = (
                    f" ({metrics.cpu.cores_physical}P/{metrics.cpu.cores_logical}L cores)"
                    if metrics.cpu.cores_physical
                    else ""
                )

                logger.info(
                    f"Published [{metrics.platform}]: "
                    f"CPU={metrics.cpu.usage_percent}%{cores_info}{gpu_info}, "
                    f"RAM={metrics.ram.used_gb}/{metrics.ram.total_gb}GB ({metrics.ram.usage_percent}%), "
                    f"Disk={metrics.disk.used_gb}/{metrics.disk.total_gb}GB ({metrics.disk.usage_percent}%){temp_info}"
                )
            else:
                logger.error("Failed to publish message")

            time.sleep(interval)

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
