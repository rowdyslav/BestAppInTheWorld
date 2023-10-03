from db_connector import OFFICES, USERS


class User:
    def __init__(self, email, password, fio) -> None:
        self.email = email
        self.password = password
        self.fio = fio

    def __str__(self) -> str:
        return self.fio

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{vars(self)}"


class OfficeWorker(User):
    def checkbox(self, breakfast: bool, dinner: bool) -> None:
        self.breakfast = breakfast
        self.dinner = dinner

    def is_breakfast(self) -> bool:
        return self.breakfast

    def is_dinner(self) -> bool:
        return self.dinner


class OfficeManager(OfficeWorker):
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

    def send_eater(self) -> dict:
        workers = OFFICES.find_one({"manager_email": self.email})["workers"]
        eats = {"breakfast": 0, "dinner": 0}
        for i in workers:
            if i.is_breakfast():
                eats["breakfast"] += 1
            if i.is_dinner():
                eats["dinner"] += 1
        return eats


class RestaurantAdmin(User):
    def add_office(self, user_email, address="Адрес оффиса по умолчанию") -> None:
        OFFICES.insert_one({"email": user_email, "address": address})

    def remove_office(self, office_name) -> None:
        OFFICES.find_one_and_delete({"name": office_name})
