from dataclasses import dataclass
from typing import Literal

from werkzeug.security import generate_password_hash, check_password_hash

from db_connector import USERS, OFFICES, DISHES
from utils import _is_login_free

type Result = str
type Success = bool


@dataclass
class Base:
    """Базовый класс для всех ролей, но по сути является Хендлером,
    тк до аунтификации данных через бд ценности не несет"""

    login: str
    password: str
    fio: str

    def _registration(
        self, role_name: Literal["worker", "admin", "cooker"]
    ) -> tuple[Result, object | None]:
        """Регистрация нового пользователя с ролью role"""

        if not _is_login_free(self.login):
            return "Логин уже занят!", None

        self.password = generate_password_hash(self.password)
        USERS.insert_one(
            {
                "login": self.login,
                "password": self.password,
                "fio": self.fio,
                "role": role_name,
            }
        )

        Role = ROLES_NAMES[role_name]
        return "Регистрация успешна!", Role(self.login, self.password, self.fio)

    def _login(self) -> tuple[Result, object | None]:
        """Логин пользователя, с проверкой по БД"""

        executor = USERS.find_one({"login": self.login})
        if not executor:
            return "Пользователь с таким логином не зарегистрирован!", None

        if not check_password_hash(executor["password"], self.password):
            return "Неверный пароль!", None

        Role = ROLES_NAMES[executor["role_name"]]
        return "Вход успешен!", Role(self.login, self.password, self.fio)


class Worker(Base):
    """Оффисный работник, который отмечает себе питание методом _send_meals"""

    def _send_meals(self, meals: dict[Literal["breakfast", "dinner"], bool]) -> None:
        """Отправка заказа с галочек с фронта"""

        print(meals)


class Admin(Base):
    """Администратор оффиса, который может добавлять и удалять работников из оффиса, а также отправляет итоговый заказ _send_meals_order"""

    def _add_worker(self, user_login: str) -> Result:
        """Добавляет работника в свой оффис"""

        ctx_user = USERS.find_one({"login": user_login})
        ctx_office = OFFICES.find_one({"admin_login": self.login})
        if not ctx_user or ctx_user["role_name"] != "worker":
            return "Сотрудник не найден!"

        OFFICES.update_one(
            {"_id": ctx_office["_id"]}, {"$push": {"workers_logins": ctx_user["login"]}}
        )
        return "Сотрудник успешно добавлен в ваш оффис!"

    def _remove_worker(self, user_login: str) -> Result:
        """Удаляет работника из своего оффиса"""

        ctx_user = USERS.find_one({"login": user_login})
        ctx_office = OFFICES.find_one({"admin_login": self.login})
        if (
            not ctx_user
            or ctx_user["role_name"] != "worker"
            or ctx_user["login"] not in ctx_office["workers_logins"]
        ):
            return "Сотрудник не найден или работает не в вашем оффисе!"

        OFFICES.update_one(
            {"admin_login": self.login},
            {"$pull": {"workers_logins": ctx_user["login"]}},
        )
        return "Сотрудник успешно удален из вашего оффиса!"

    def _add_dish(self, title, description, structure) -> Result:
        ctx_office = OFFICES.find_one({"admin_login": self.login})
        if DISHES.find_one({"title": title}):
            return "Блюдо с таким названием уже есть!"
        else:
            DISHES.insert_one(
                {
                    "title": title,
                    "description": description,
                    "office": ctx_office["_id"],
                    "structure": structure,
                    "photo": "photo",
                }
            )
            return "Блюдо успешно добавлено"

    # Надо полностью переписать
    def _get_meals_order(self) -> dict[str, int]:
        """Получить итоговый заказ со всего оффиса"""

        workers = OFFICES.find_one({"admin_login": self.login})["workers_logins"]
        meals = {"breakfasts": 0, "dinners": 0, "eaters_count": 0}

        # for i in workers:
        #     if i.is_breakfast():  # пока абстрактно
        #         meals["breakfasts"] += 1
        #     if i.is_dinner():  # пока абстрактно
        #         meals["dinners"]
        #     meals["eaters_count"] += 1
        return meals

    def _send_meals_order(self, meals: dict[Literal["breakfasts", "dinners"], int]):
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
