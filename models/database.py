from pymongo import MongoClient
from configs.envconfig import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['main']

def get_collection(name):
    return db[name]
