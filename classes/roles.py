from db_connector import OFFICES, USERS
from classes.utils import Office


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
    def __init__(self, email, password, fio, office: Office) -> None:
        super().__init__(email, password, fio)
        self.own_office = office

    def add_office_worker(self, user_email) -> None:
        self.own_office.workers.append(USERS.find({"email": user_email}))

    def remove_office_worker(self, user_email) -> None:
        self.own_office.workers.remove(USERS.find({"email": user_email}))

    def send_eater(self) -> dict:
        workers = self.own_office.workers
        eats = {"breakfast": 0, "dinner": 0}
        for i in workers:
            if i.is_breakfast():
                eats["breakfast"] += 1
            if i.is_dinner():
                eats["dinner"] += 1
        return eats


class RestaurantAdmin(User):
    """Должна быть логика добавения оффиса со своим менеджером"""

    def add_office(self, user_email, address="Адрес оффиса по умолчанию") -> None:
        OFFICES.insert_one(vars(Office(user_email, address)))

    def remove_office(self, office_name) -> None:
        OFFICES.find_one_and_delete({"id": office_name})
