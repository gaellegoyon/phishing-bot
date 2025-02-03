# Dockerfile
FROM python:3.11-slim

# Désactiver le buffering Python pour voir les logs en temps réel
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src/ ./src

# Exposer le port pour Socket Mode
EXPOSE 3000

# Lancer simultanément le listener Slack en Socket Mode et le scheduler
CMD ["sh", "-c", \
    "echo '⚙️  [DEBUG] Démarrage du listener Slack (Socket Mode)...'; \
    python -u src/bot.py & \
    echo '📆 [DEBUG] Démarrage du scheduler...'; \
    python -u src/scheduler.py"]
