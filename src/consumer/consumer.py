import time
import uuid
from typing import Any

import paho.mqtt.client as mqtt

from common.config.mqtt_config import MQTTConfig
from common.utils.logger import setup_logger
from common.utils.mqtt_client import MQTTClient
from sensor.model import SystemMetrics

logger = setup_logger("Consumer")
config = MQTTConfig()


def on_message(_client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage) -> None:
    """Handle incoming MQTT messages"""
    try:
        # Deserialize JSON to SystemMetrics model
        message_json = msg.payload.decode("utf-8")
        metrics = SystemMetrics.from_json(message_json)

        # Format additional metrics
        gpu_info = (
            f", GPU={metrics.gpu[0].load_percent}%" if metrics.gpu else ", GPU=N/A"
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

        # Log comprehensive metrics
        logger.info(
            f"Metrics [{metrics.platform}]: "
            f"CPU={metrics.cpu.usage_percent}%{cores_info}{gpu_info}, "
            f"RAM={metrics.ram.used_gb}/{metrics.ram.total_gb}GB ({metrics.ram.usage_percent}%), "
            f"Disk={metrics.disk.used_gb}/{metrics.disk.total_gb}GB ({metrics.disk.usage_percent}%){temp_info}, "
            f"Timestamp={metrics.timestamp}"
        )

    except Exception as e:
        logger.error(f"Failed to parse message: {e}")


def start_consumer() -> None:
    # Generate unique client ID to allow multiple consumer instances
    client_id = f"protexai-consumer-{uuid.uuid4().hex[:8]}"

    logger.info(
        f"MQTT Broker: {config.BROKER_HOST}:{config.BROKER_PORT} Topic: {config.TOPIC} Client ID: {client_id}`"
    )

    try:
        with MQTTClient(
            client_id=client_id,
            logger=logger,
            on_message=on_message,
        ) as client:
            client.subscribe(config.TOPIC)
            logger.info("Consumer running (Press Ctrl+C to stop)")
            while True:
                time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")

    except Exception:
        logger.exception("ConsumerError")


if __name__ == "__main__":
    start_consumer()
