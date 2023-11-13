from pymongo.mongo_client import MongoClient
from icecream import ic

DB_URL = "mongodb+srv://rowdyslav:228doxy228@cluster0.736skbi.mongodb.net/?retryWrites=true&w=majority"

try:
    print(f"Подключение к MongoDB...")
    DB_CLIENT = MongoClient(DB_URL)
except Exception as e:
    print("Ошибка при подключении!")
    ic(e)
    exit()
else:
    print("Успешно!")

    CUBEFOOD_DB = DB_CLIENT["CubeFood"]

    OFFICES = CUBEFOOD_DB["offices"]
    USERS = CUBEFOOD_DB["users"]
    DISHES = CUBEFOOD_DB["dishes"]
