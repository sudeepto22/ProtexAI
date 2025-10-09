import os


class MQTTConfig:
    """MQTT broker configuration"""
    
    BROKER_HOST = os.getenv('MQTT_BROKER_HOST', 'localhost')
    BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', '1883'))
    TOPIC = os.getenv('MQTT_TOPIC', 'test/topic')
    KEEPALIVE = 60
    QOS = 0

