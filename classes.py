from db import USERS


class Role:
    def __init__(self, fio) -> None:
        self.fio = fio

    def __str__(self) -> str:
        return self.fio

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{vars(self)}"


class User(Role):
    pass


class Admin(User):
    def add_user(self, user_email):
        pass

    def remove_user(self, user_email):
        pass


class Cooker(Role):
    """Должна быть логика добавения оффиса со своим менеджером"""

    def add_admin(self, admin_email):
        pass

    def remove_admin(self, admin_email):
        pass
