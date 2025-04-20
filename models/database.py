from pymongo import MongoClient
from configs.envconfig import MONGO_URI
import os

env = os.getenv("FLASK_ENV", "development")
client = MongoClient(MONGO_URI)

if env == "testing":
    db = client["tests"]
else:
    db = client["main"]
def get_collection(name):
    return db[name]
