#!/bin/bash

echo "======================"
echo "ProtexAI Local Setup"
echo "======================"
echo "Stopping Docker containers"
docker-compose down
echo "Starting Mosquitto broker and MongoDB"
docker-compose up -d mosquitto mongodb
