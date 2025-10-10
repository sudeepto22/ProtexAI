import logging

from slack_sdk import WebClient
from slack_sdk.web import SlackResponse

from common.config.slack_config import SlackConfig
from sensor.model import SystemMetrics


def send_slack_message(
    text: str,
    channel: str,
    blocks: list | None = None,
    attachments: list | None = None,
) -> SlackResponse:
    try:
        client = WebClient(token=SlackConfig.BOT_TOKEN)
        return client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=blocks,
            attachments=attachments,
        )
    except Exception:
        raise


def send_slack_notification(
    metrics: SystemMetrics, logger: logging.Logger | None = None
) -> None:
    """Send notification to Slack"""
    if logger is None:
        logger = logging.getLogger("SlackNotification")
    try:
        message_payload = format_metrics_for_slack(metrics)
        response = send_slack_message(**message_payload)

        if not response["ok"]:
            logger.error(f"Failed to send Slack notification: {response['error']}")
        else:
            logger.info(f"Notification sent to Slack: {response['ts']}")

    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")


def send_critical_alert(alert: dict[str, float]) -> None:
    message = ""
    if alert:
        for key, value in alert.items():
            message += f"\n*{key}*: {value}%"
    send_slack_message(message, SlackConfig.ALERT_CHANNEL)


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
