from pymongo import MongoClient
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

USERNAME = os.getenv("MONGO_DB_USERNAME")
DB_PWD = os.getenv("MONGO_DB_PWD")
DB_NAME = os.getenv("MONGO_DB_NAME", "smartsupply_logs")
MONGO_URI = f"mongodb+srv://{USERNAME}:{urllib.parse.quote_plus(DB_PWD)}@smartsupply-cluster.vrvdnqj.mongodb.net/?appName=SmartSupply-Cluster"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
# Purpose: trace user –> agent –> tool decision
conversation_logs = db.conversation_logs

# Purpose: trace inventory-changing actions
audit_logs = db.audit_logs

def test_connection():
    """Simple ping to verify connection"""
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False