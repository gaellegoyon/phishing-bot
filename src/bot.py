import re
import os
import sys
from datetime import datetime
from slack_bolt import App as SlackApp
from slack_bolt.adapter.socket_mode import SocketModeHandler
from vt_client import check_url
from database import scans

print("⚙️  [DEBUG] Slack listener démarré (Socket Mode)...", flush=True)

SLACK_BOT_TOKEN   = os.getenv('SLACK_BOT_TOKEN')
SLACK_SIGN_SECRET = os.getenv('SLACK_SIGNING_SECRET')
SLACK_APP_TOKEN   = os.getenv('SLACK_APP_TOKEN')

if not (SLACK_BOT_TOKEN and SLACK_SIGN_SECRET and SLACK_APP_TOKEN):
    print("❌ Variables d'environnement Slack manquantes !", file=sys.stderr)
    sys.exit(1)

slack_app = SlackApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGN_SECRET)

URL_REGEX = r'https?://[\w\-\.\?\,\'/\\+&%\$#_]+'

@slack_app.event("message")
def handle_slack_events(body, say):
    print("🔔 [DEBUG] Event Slack reçu", flush=True)
    event   = body.get('event', {})
    user    = event.get('user')
    text    = event.get('text', '')
    channel = event.get('channel')
    ts      = datetime.utcnow()
    urls    = re.findall(URL_REGEX, text)
    for url in urls:
        print(f"🔍 [DEBUG] Scanning URL {url}", flush=True)
        result = check_url(url)
        record = {
            'ts': ts,
            'platform': 'slack',
            'user_id': user,
            'channel_id': channel,
            **result
        }
        scans.insert_one(record)
        if result.get('malicious', 0) > 0:
            say(f"⚠️ <@{user}> Lien malveillant détecté: {result['permalink']}")

if __name__ == "__main__":
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()

