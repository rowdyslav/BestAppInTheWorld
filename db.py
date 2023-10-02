from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

DB_URL = getenv("MONGODB_URL")
CLIENT = MongoClient(DB_URL, server_api=ServerApi("1"))
DB = CLIENT[config["db_name"]]
COLLECTION = DB[config["coll_name"]]
