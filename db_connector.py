from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

DB_URL = "mongodb+srv://rowdyslav:228doxy228@cluster0.736skbi.mongodb.net/?retryWrites=true&w=majority"
DB_CLIENT = MongoClient(DB_URL, server_api=ServerApi("1"))
CUBEFOOD_DB = DB_CLIENT["CubeFood"]

OFFICES = CUBEFOOD_DB["offices"]
USERS = CUBEFOOD_DB["users"]
