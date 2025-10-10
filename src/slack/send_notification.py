import logging

from slack_sdk import WebClient

from common.config.slack_config import SlackConfig
from sensor.model import SystemMetrics

logger = logging.getLogger("SlackNotification")


def send_slack_notification(metrics: SystemMetrics) -> None:
    """Send notification to Slack"""
    try:
        if not SlackConfig.BOT_TOKEN:
            logger.warning("SLACK_BOT_TOKEN not configured, skipping notification")
            return
            
        client = WebClient(token=SlackConfig.BOT_TOKEN)
        message_payload = format_metrics_for_slack(metrics)
        response = client.chat_postMessage(**message_payload)

        if not response["ok"]:
            logger.error(f"Failed to send notification: {response['error']}")
        else:
            logger.info(f"Notification sent to Slack: {response['ts']}")

    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")


def format_metrics_for_slack(metrics: SystemMetrics) -> dict:
    """Format metrics as Slack message"""

    # Format CPU info
    cpu_text = f"*CPU:* {metrics.cpu.usage_percent}%"
    if metrics.cpu.cores_physical:
        cpu_text += (
            f" ({metrics.cpu.cores_physical}P/{metrics.cpu.cores_logical}L cores)"
        )

    # Format GPU info
    gpu_text = "*GPU:* N/A"
    if metrics.gpu and len(metrics.gpu) > 0:
        gpu = metrics.gpu[0]
        gpu_text = (
            f"*GPU:* {gpu.load_percent}% load, {gpu.memory_usage_percent}% memory"
        )
        if gpu.temperature_c:
            gpu_text += f", {gpu.temperature_c}°C"

    # Format RAM info
    ram_text = f"*RAM:* {metrics.ram.used_gb:.1f}GB / {metrics.ram.total_gb:.1f}GB ({metrics.ram.usage_percent}%)"

    # Format Disk info
    disk_text = f"*Disk:* {metrics.disk.used_gb:.1f}GB / {metrics.disk.total_gb:.1f}GB ({metrics.disk.usage_percent}%)"

    temps = []
    if metrics.temperature and len(metrics.temperature) > 0:
        for temp in metrics.temperature:
            temps.append(f"{temp.label} {temp.temperature_c}°C")

    # Create Slack blocks
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*System Metrics Report* - _{metrics.platform}_",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": cpu_text},
                {"type": "mrkdwn", "text": gpu_text},
                {"type": "mrkdwn", "text": ram_text},
                {"type": "mrkdwn", "text": disk_text},
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Termperature:* {'N/A' if not temps else '\0'}",
                },
                {
                    "type": "mrkdwn",
                    "text": "\0",
                },
            ]
            + [{"type": "mrkdwn", "text": temp} for temp in temps],
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Time:* {metrics.timestamp}"},
            ],
        },
    ]

    return {
        "channel": SlackConfig.CHANNEL,
        "text": f"System Metrics - CPU: {metrics.cpu.usage_percent}%",
        "blocks": blocks,
        "attachments": [],
    }
