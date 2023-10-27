from db_connector import USERS, OFFICES
from roles.base import Base


class Admin(Base):
    def _add_worker(self, user_login: str) -> None:
        ctx_user = USERS.find_one({"login": user_login})
        ctx_office = OFFICES.find_one({"admin_login": self.login})
        USERS.update_one(
            {"_id": ctx_user["_id"]}, {"$set": {"office_name": ctx_office["name"]}}
        )
        OFFICES.update_one(
            {"_id": ctx_office["_id"]}, {"$push": {"workers_logins": ctx_user["login"]}}
        )

    def _remove_worker(self, user_login: str) -> None:
        ctx_user = USERS.find_one({"login": user_login})
        USERS.update_one({"_id": ctx_user["_id"]}, {"$set": {"office_name": None}})
        OFFICES.update_one(
            {"admin_login": self.login},
            {"$pull": {"workers_logins": ctx_user["login"]}},
        )

    def _get_meals_order(self) -> dict:
        workers = OFFICES.find_one({"admin_login": self.login})["workers"]
        eats = {"breakfast": 0, "dinner": 0}
        for i in workers:
            if i.is_breakfast():  # пока абстрактно
                eats["breakfast"] += 1
            if i.is_dinner():  # пока абстрактно
                eats["dinner"] += 1
        return eats

    def _send_meals_order(self):
        ...
