import os

from dotenv import load_dotenv


class SlackConfig:
    """Slack configuration"""

    load_dotenv()

    BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    CHANNEL = os.getenv("SLACK_CHANNEL", "#notifs")
    ALERT_CHANNEL = os.getenv("SLACK_ALERT_CHANNEL", "#alerts")
    SEND_DURATION_SECONDS = float(os.getenv("SLACK_SEND_DURATION_SECONDS", 60))
