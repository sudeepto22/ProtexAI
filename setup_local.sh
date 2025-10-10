#!/bin/bash

echo "======================"
echo "ProtexAI Local Setup"
echo "======================"
echo "Stopping Docker containers"
docker-compose down
echo "Starting Mosquitto broker"
docker-compose up -d mosquitto
