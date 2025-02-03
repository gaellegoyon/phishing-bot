import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    VT_API_KEY: str = os.getenv('VT_API_KEY')
    SLACK_BOT_TOKEN: str = os.getenv('SLACK_BOT_TOKEN')
    SLACK_SIGNING_SECRET: str = os.getenv('SLACK_SIGNING_SECRET')
    MONGODB_URI: str = os.getenv('MONGODB_URI')

settings = Settings()