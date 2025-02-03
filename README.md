# PhishingBot

Un bot de détection de phishing pour Slack, analysant les liens partagés via l’API VirusTotal, alertant en temps réel et générant un rapport quotidien.

## Fonctionnalités

- **Slack Socket Mode** : réception des messages sans exposer de webhook public
- **Analyse VirusTotal** : soumission et récupération des résultats (GET /urls, POST /urls, GET /analyses)
- **Stockage MongoDB** : enregistrement des scans avec timestamp réel (`datetime`)
- **Rapport quotidien** : résumé des analyses et top 5 des URLs malveillantes envoyé automatiquement à minuit (CET)
- **Mode manuel** : `python src/scheduler.py run-now` pour déclencher immédiatement le rapport

## Prérequis

- Docker & Docker Compose
- Compte VirusTotal avec clé API (`VT_API_KEY`)
- Cluster MongoDB (`MONGODB_URI`)
- Workspace Slack avec une app configurée (Socket Mode, scopes et events)

## Installation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/gaellegoyon/phishing-bot.git
   cd phishing-bot
   ```

2. Copiez le template d’environnement et configurez vos clefs :

   ```bash
   cp .env.example .env
   # Éditez .env pour ajouter :
   # SLACK_BOT_TOKEN=...
   # SLACK_SIGNING_SECRET=...
   # SLACK_APP_TOKEN=...
   # VT_API_KEY=...
   # MONGODB_URI=...
   # ADMIN_CHANNEL=#tous-phishingbot
   ```

3. Lancez les conteneurs :

   ```bash
   docker-compose up --build -d
   docker-compose logs -f
   ```

## Usage

- **Tester le listener** :
  Envoyez un message dans Slack, par ex.

  ```
  @PhishingBot check http://example.com
  ```

  Vous verrez en logs :

  ```
  🔔 [DEBUG] Event Slack reçu
  🔍 [DEBUG] Scanning URL http://example.com
  ```

- **Rapport manuel** :

  ```bash
  docker-compose exec -T bot python src/scheduler.py run-now
  ```

  Le rapport sera posté dans le canal défini par `ADMIN_CHANNEL`.
