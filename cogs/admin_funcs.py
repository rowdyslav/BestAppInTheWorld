from db_connector import USERS, OFFICES

# pyright: reportOptionalSubscript=false


def _add_worker(admin, user_email) -> None:
    ctx_user = USERS.find_one({"email": user_email})
    ctx_office = OFFICES.find_one({"admin_email": admin["email"]})
    USERS.update_one(
        {"_id": ctx_user["_id"]}, {"$set": {"office_name": ctx_office["name"]}}
    )
    OFFICES.update_one(
        {"_id": ctx_office["_id"]}, {"$push": {"workers_emails": ctx_user["email"]}}
    )


def _remove_worker(admin, user_email) -> None:
    ctx_user = USERS.find_one({"email": user_email})
    USERS.update_one({"_id": ctx_user["_id"]}, {"$set": {"office_name": None}})
    OFFICES.update_one(
        {"admin_email": admin["email"]},
        {"$pull": {"workers_emails": ctx_user["email"]}},
    )


def _send_order(admin) -> dict:
    workers = OFFICES.find_one({"admin_email": admin["email"]})["workers"]
    eats = {"breakfast": 0, "dinner": 0}
    for i in workers:
        if i.is_breakfast():
            eats["breakfast"] += 1
        if i.is_dinner():
            eats["dinner"] += 1
    return eats
