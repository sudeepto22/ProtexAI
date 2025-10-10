# ProtexAI

A real-time system monitoring and alerting platform that collects system metrics, publishes them via MQTT, stores them in MongoDB, and provides visualizations through a web UI with Slack notifications.

## Architecture

- **Producer**: Collects and publishes system metrics to MQTT
- **Consumer**: Subscribes to MQTT topics, stores metrics in MongoDB, sends Slack notifications
- **API**: FastAPI service to query stored metrics
- **UI Consumer**: React-based dashboard for real-time metric visualization using MQTT WebSocket and the API
- **Infrastructure**: MQTT (Mosquitto), MongoDB

## Prerequisites

- **For Docker**: Docker & Docker Compose
- **For Local**: Python 3.12+, Node.js 20+, Docker (for MQTT & MongoDB)

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```bash
# MongoDB Configuration (Required)
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your_secure_password

# Slack Configuration (Required for notifications)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL=#notifs
SLACK_ALERT_CHANNEL=#alerts
SLACK_SEND_DURATION_SECONDS=30
```

## Installation & Running

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Services will be available at:**

- UI: http://localhost:3000
- API: http://localhost:8000
- MQTT: localhost:1883 (TCP), localhost:9001 (WebSocket)
- MongoDB: localhost:27017

### Option 2: Local Development

```bash
# Make the script executable
chmod +x setup_local.sh

# Run all services
./setup_local.sh
```

This script will:

1. Start MQTT broker and MongoDB containers
2. Create a Python virtual environment
3. Install all dependencies
4. Start Producer, Consumer, API, and UI services

**Services will be available at:**

- UI: http://localhost:3000
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

**To stop all services:** Press `Ctrl+C`

## Assumptions

- The following ports are available
  - 1883 (MQTT)
  - 9001 (MQTT WebSocket)
  - 27017 (MongoDB)
  - 8000 (API)
  - 3000 (UI)
- Slack bot token has permissions to post to specified channels
- Docker daemon is running for both deployment options
- System has sufficient resources to run all services simultaneously
- For local setup, MQTT and MongoDB run in Docker while application services run on host

## API Endpoints

- `GET /metrics/latest?limit=10` - Retrieve latest metrics from MongoDB

## Logs

- **Docker**: `docker-compose logs -f [service_name]`
- **Local**: Available in `src/logs/` directory
