import random
import time
import uuid
from typing import Any

import paho.mqtt.client as mqtt
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from common.config.mqtt_config import MQTTConfig
from common.config.slack_config import SlackConfig
from common.utils.logger import setup_logger
from common.utils.mongodb_client import MongoDBClientManager
from common.utils.mqtt_client import MQTTClient
from sensor.model import SystemMetrics
from slack.send_notification import send_slack_notification

logger = setup_logger("Consumer")
config = MQTTConfig()

MONGO_COLLECTION: Collection | None = None
MAX_RETRIES = 5

NOTIFICATION_TIMER = time.time()


def insert_to_database(metrics: SystemMetrics) -> None:
    """Insert metrics to MongoDB"""
    if MONGO_COLLECTION is not None:
        result = MONGO_COLLECTION.insert_one(metrics.to_dict())
        logger.info(f"Stored to MongoDB with ID: {result.inserted_id}")


def on_message(_client: mqtt.Client, _userdata: Any, msg: mqtt.MQTTMessage) -> None:
    """Handle incoming MQTT messages and store to MongoDB"""
    global NOTIFICATION_TIMER
    try:
        message_json = msg.payload.decode("utf-8")
        metrics = SystemMetrics.from_json(message_json)

        logger.info(f"Metrics: {metrics}")

        insert_to_database(metrics)
        if NOTIFICATION_TIMER + SlackConfig.SEND_DURATION_SECONDS > time.time():
            NOTIFICATION_TIMER = time.time()
            return
        send_slack_notification(metrics)

    except Exception as e:
        logger.error(f"Failed to process message: {e}")


def start_consumer() -> None:
    global MONGO_COLLECTION

    # Generate unique client ID to allow multiple consumer instances
    client_id = f"protexai-consumer-{uuid.uuid4().hex[:8]}"

    logger.info(
        f"MQTT Broker: {config.BROKER_HOST}:{config.BROKER_PORT} Topic: {config.TOPIC} Client ID: {client_id}"
    )

    # Try to connect with retries
    for attempt in range(MAX_RETRIES):
        try:
            with (
                MongoDBClientManager(logger) as collection,
                MQTTClient(client_id, logger, on_message) as client,
            ):
                MONGO_COLLECTION = collection
                logger.info("MongoDB and MQTT connected successfully")

                client.subscribe(config.TOPIC)
                logger.info("Consumer running (Press Ctrl+C to stop)")

                try:
                    while True:
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    logger.info("Consumer stopped by user")
            return

        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
            return

        except ConnectionFailure as e:
            if attempt < MAX_RETRIES - 1:
                delay = 2**attempt
                jitter = random.uniform(0, delay * 0.3)  # Upto 30% jitter
                # Add jitter to delay
                wait_time = delay + jitter
                logger.warning(
                    f"Connection attempt {attempt + 1} failed: {e}, retrying in {wait_time}s"
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"Max retries reached. Consumer requires MongoDB to run. Error: {e}"
                )
                raise


if __name__ == "__main__":
    start_consumer()
