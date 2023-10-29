from dataclasses import dataclass
from typing import Literal, Optional

from db_connector import USERS, OFFICES
from utils import _is_login_free


@dataclass
class Base:
    """Базовый класс для всех ролей, но по сути является Хендлером,
    тк до аунтификации данных через бд ценности не несет"""

    login: str
    password: str
    fio: str

    def _registration(
        self, role: Literal["worker", "admin", "cooker"]
    ) -> tuple[str, object | None]:
        """Регистрация нового пользователя с ролью role"""

        if not _is_login_free(self.login):
            return "Логин уже занят!", None

        USERS.insert_one(
            {
                "login": self.login,
                "password": self.password,
                "fio": self.fio,
                "role": role,
            }
        )

        cls = ROLES_NAMES.get(role)
        if not cls:
            return "Нету роли!", None

        user = cls(self.login, self.password, self.fio)

        return "Регистрация успешна!", user

    def _login(self) -> tuple[str, object | None]:
        """Логин пользователя, с проверкой по БД"""

        executor = USERS.find_one({"login": self.login})
        if not executor:
            return "Пользователь с таким логином не зарегистрирован!", None

        if executor["password"] != self.password:
            return "Неверный пароль!", None

        cls = ROLES_NAMES.get(executor["role"])
        if not cls:
            return "Нету роли!", None

        user = cls(self.login, self.password, self.fio)
        return (
            "Вход успешен!",
            user,
        )


class Worker(Base):
    """Оффисный работник, который отмечает себе питание методом _send_meals"""

    def _send_meals(self, meals: dict[Literal["breakfast", "dinner"], bool]) -> None:
        """Отправка заказа с галочек с фронта"""

        print(meals)


class Admin(Base):
    """Администратор оффиса, который может добавлять и удалять работников из оффиса, а также отправляет итоговый заказ _send_meals_order"""

    def _add_worker(self, user_login: str) -> None:
        """Добавляет работника в свой оффис"""

        ctx_user = USERS.find_one({"login": user_login})
        ctx_office = OFFICES.find_one({"admin_login": self.login})
        USERS.update_one(
            {"_id": ctx_user["_id"]}, {"$set": {"office_name": ctx_office["name"]}}
        )
        OFFICES.update_one(
            {"_id": ctx_office["_id"]}, {"$push": {"workers_logins": ctx_user["login"]}}
        )

    def _remove_worker(self, user_login: str) -> None:
        """Удаляет работника из своего оффиса"""

        ctx_user = USERS.find_one({"login": user_login})
        USERS.update_one({"_id": ctx_user["_id"]}, {"$set": {"office_name": None}})
        OFFICES.update_one(
            {"admin_login": self.login},
            {"$pull": {"workers_logins": ctx_user["login"]}},
        )

    def _get_meals_order(self) -> dict:
        """Получить итоговый заказ со всего оффиса"""

        workers = OFFICES.find_one({"admin_login": self.login})["workers"]
        eats = {"breakfast": 0, "dinner": 0}
        for i in workers:
            if i.is_breakfast():  # пока абстрактно
                eats["breakfast"] += 1
            if i.is_dinner():  # пока абстрактно
                eats["dinner"] += 1
        return eats

    def _send_meals_order(self):
        """Отправить заказ в ресторан"""

        ...


class Cooker(Base):
    """Администратор ресторана, добавляет оффисы для обслуживания, вместе с виртуальными учетками их админов"""

    def _add_office(
        self,
        admin_login: str,
        admin_password: str,
        admin_fio: str,
        office_name: str,
        office_address: str,
    ) -> None:
        """Добавляет виртуальную учетку админа и связанный с ним оффис в бд"""

        Base(admin_login, admin_password, admin_fio)._registration("admin")

        OFFICES.insert_one(
            {
                "name": office_name,
                "admin_login": admin_login,
                "address": office_address,
                "workers_logins": [],
            }
        )

    def _remove_office(self, admin_login) -> None:
        """Удаляет виртуальную учетку админа и связанный с ним оффис из бд"""
        USERS.find_one_and_delete({"login": admin_login})
        OFFICES.find_one_and_delete({"admin_login": admin_login})


ROLES_NAMES = {i.__name__.lower(): i for i in (Worker, Admin, Cooker)}
