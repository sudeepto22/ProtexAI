#!/bin/bash

# Gracefully shutdown all services
cleanup() {
    echo ""
    echo "======================"
    echo "Shutting down ProtexAI..."
    echo "======================"
    
    # Kill all background processes
    if [ ! -z "$PRODUCER_PID" ]; then
        echo "Stopping Producer..."
        kill $PRODUCER_PID 2>/dev/null
    fi
    
    if [ ! -z "$CONSUMER_PID" ]; then
        echo "Stopping Consumer..."
        kill $CONSUMER_PID 2>/dev/null
    fi
    
    if [ ! -z "$API_PID" ]; then
        echo "Stopping API..."
        kill $API_PID 2>/dev/null
    fi
    
    if [ ! -z "$UI_PID" ]; then
        echo "Stopping UI..."
        kill $UI_PID 2>/dev/null
    fi
    
    # Stop Docker containers
    echo "Stopping Docker containers..."
    docker-compose down
    
    echo "Cleanup complete!"
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "======================"
echo "ProtexAI Local Setup"
echo "======================"

# Stop any running containers first
echo "Stopping Docker containers..."
docker-compose down

# Start Docker services
echo "Starting MQTT broker and MongoDB..."
docker-compose up -d mosquitto mongodb

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 3

# Activate virtual environment
if [ -z  "venv" ]; then
    echo "Creating virtual environment" 
    python -m venv venv
fi
source venv/bin/activate

echo "Installing dependencies..."
pip install -r src/producer/requirements.txt
pip install -r src/consumer/requirements.txt
pip install -r src/api/requirements.txt

echo ""
echo "Starting all services..."
echo "======================"

# Start Producer
echo "Starting Producer..."
cd src
PYTHONPATH=$(pwd) python producer/producer.py > logs/producer.log 2>&1 &
PRODUCER_PID=$!
cd ..

# Start Consumer
echo "Starting Consumer..."
cd src
PYTHONPATH=$(pwd) python consumer/consumer.py > logs/consumer.log 2>&1 &
CONSUMER_PID=$!
cd ..

# Start API
echo "Starting API..."
cd src
PYTHONPATH=$(pwd) python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
API_PID=$!
cd ..

# Start UI Consumer
echo "Starting UI Consumer..."
cd src/ui_consumer
REACT_APP_MQTT_BROKER=ws://localhost:9001 REACT_APP_MQTT_TOPIC=test/topic npm start > ../logs/ui.log 2>&1 &
UI_PID=$!
cd ../..

echo ""
echo "======================"
echo "All services running!"
echo "======================"
echo "Producer:     http://localhost (PID: $PRODUCER_PID)"
echo "Consumer:     http://localhost (PID: $CONSUMER_PID)"
echo "API:          http://localhost:8000 (PID: $API_PID)"
echo "UI:           http://localhost:3000 (PID: $UI_PID)"
echo ""
echo "Press Ctrl+C to stop all services"
echo "Logs are available in the logs/ directory"
echo "======================"

wait
