from pymongo.mongo_client import MongoClient
from icecream import ic
from gridfs import GridFS


DB_URL = "mongodb+srv://rowdyslav:228doxy228@cluster0.736skbi.mongodb.net/?retryWrites=true&w=majority"


try:
    DB_CLIENT = MongoClient(DB_URL)
    print(f"Подключение к MongoDB из ...")
except Exception as e:
    print("Ошибка при подключении!")
    ic(e)
    exit()
else:
    CUBEFOOD_DB = DB_CLIENT["CubeFood"]
    USERS = CUBEFOOD_DB["users"]
    DISHES = CUBEFOOD_DB["dishes"]
    ORDERS = CUBEFOOD_DB["orders"]
    FILES = GridFS(CUBEFOOD_DB, collection="dishes")
    print("Успешно!")
