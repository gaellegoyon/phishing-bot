#!/bin/sh
set -e

export PYTHONUNBUFFERED=1

echo "⚙️  [DEBUG] Démarrage du listener Slack (Socket Mode)..."
python -u src/bot.py &

echo "📆 [DEBUG] Démarrage du scheduler..."
python -u src/scheduler.py