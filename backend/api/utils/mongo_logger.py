# backend/api/utils/mongo_logger.py

from datetime import datetime
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def log_event(event_type, data):
    """Store logs with timestamps and context."""
    entry = {
        "event": event_type,
        "timestamp": datetime.utcnow(),
        "details": data,
    }
    collection.insert_one(entry)
