from typing import Optional
from db_connector import USERS

from roles.base import Base
from utils import _is_login_free


class User(Base):
    def _registration(self) -> tuple[str, bool]:
        if not _is_login_free(self.login):
            return "Логин уже занят!", False
        USERS.insert_one(
            {
                "login": self.login,
                "password": self.password,
                "fio": self.fio,
                "role": "user",
            }
        )
        return "Регистрация успешна!", True

    def send_meals(self):
        ...
