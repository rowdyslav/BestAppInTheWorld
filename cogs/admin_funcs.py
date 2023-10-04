from db_connector import USERS, OFFICES


def add_office_worker(self, user_email) -> None:
    ctx_user = USERS.find_one({"email": user_email})
    ctx_office = OFFICES.find_one({"manager_email": self.email})
    USERS.update_one(
        {"_id": ctx_user["_id"]}, {"$set": {"office_name": ctx_office["name"]}}
    )
    OFFICES.update_one(
        {"_id": ctx_office["_id"]}, {"$push": {"workers_emails": ctx_user["email"]}}
    )


def remove_office_worker(self, user_email) -> None:
    ctx_user = USERS.find_one({"email": user_email})
    USERS.update_one({"_id": ctx_user["_id"]}, {"$set": {"office_name": None}})


def send_order(self) -> dict:
    workers = OFFICES.find_one({"manager_email": self.email})["workers"]
    eats = {"breakfast": 0, "dinner": 0}
    for i in workers:
        if i.is_breakfast():
            eats["breakfast"] += 1
        if i.is_dinner():
            eats["dinner"] += 1
    return eats
