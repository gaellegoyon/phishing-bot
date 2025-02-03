from pymongo import MongoClient
from config import settings

client = MongoClient(settings.MONGODB_URI)
db = client.phishing
scans = db.scans