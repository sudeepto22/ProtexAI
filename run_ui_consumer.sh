#!/bin/bash
cd src/ui_consumer
REACT_APP_MQTT_BROKER=ws://localhost:9001 REACT_APP_MQTT_TOPIC=test/topic npm start
