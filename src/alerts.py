from config import settings
from slack_bolt import App as SlackApp

# Slack
slack_app = SlackApp(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET
)

async def alert_slack(channel: str, text: str):
    slack_app.client.chat_postMessage(channel=channel, text=text)
