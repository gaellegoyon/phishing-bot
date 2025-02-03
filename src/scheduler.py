from apscheduler.schedulers.blocking import BlockingScheduler
from database import scans
from alerts import alert_slack
from datetime import datetime, timedelta
import asyncio
import os
import sys

# Debug au démarrage
print("📆 [DEBUG] Scheduler démarré...", flush=True)

scheduler = BlockingScheduler(timezone="Europe/Paris")
ADMIN_CHANNEL = os.getenv('ADMIN_CHANNEL')

async def send_report():
    since = datetime.utcnow() - timedelta(days=1)
    total = scans.count_documents({'ts': {'$gte': since}})
    malwares = scans.count_documents({
        'ts': {'$gte': since}, 'malicious': {'$gt': 0}
    })
    pipeline = [
        {'$match': {'ts': {'$gte': since}, 'malicious': {'$gt': 0}}},
        {'$group': {'_id': '$url', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}, {'$limit': 5}
    ]
    top = list(scans.aggregate(pipeline))
    text = (
        f"*Rapport quotidien de phishing*\n"
        f"Total d'analyses: {total}\n"
        f"Malwares détectés: {malwares}\n\n"
        f"*Top 5 des URLs malveillantes:*\n"
    )
    for entry in top:
        text += f"- {entry['_id']} (Détections: {entry['count']})\n"
    text += "\nPour plus de détails, consultez le tableau de bord."
    await alert_slack(ADMIN_CHANNEL, text)


def daily_report():
    print("⏱️  [DEBUG] Lancement manuel du rapport quotidien", flush=True)
    asyncio.run(send_report())

if __name__ == "__main__":
    # Mode manuel
    if len(sys.argv) > 1 and sys.argv[1] == 'run-now':
        daily_report()
        sys.exit(0)
    # Cron quotidien
    scheduler.add_job(daily_report, 'cron', hour=0, minute=0)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()