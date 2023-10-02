from db import USERS
from roles import User, Admin, Cooker

classes = {"user": User, "admin": Admin, "cooker": Cooker}


inits_users = {"users": [], "admins": [], "cookers": []}
for user in USERS.find():
    inits_users[user["role"] + "s"].append(classes[user["role"]](user["fio"]))
print(inits_users)
