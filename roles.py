from dataclasses import dataclass

from io import BytesIO
from base64 import b64encode
from bson import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

from db_conn import USERS, DISHES, FILES, ORDERS
from utils import _is_login_free

from datetime import date as d
from datetime import datetime as dt

from itertools import cycle

from icecream import ic

type LogStr = str


@dataclass
class User:
    """Базовый класс для всех ролей"""

    login: str
    password: str

    def _registration(self, fio) -> tuple[LogStr, bool]:
        """Регистрация нового пользователя с ролью role"""

        if not _is_login_free(self.login):
            return "Логин уже занят!", False

        self.password = generate_password_hash(self.password)
        USERS.insert_one(
            {
                "login": self.login,
                "password": self.password,
                "fio": fio,
                "role": None,
                "parent": None,
                "tg_id": None,
            }
        )

        return (
            "Регистрация успешна! Теперь администратор должен назначить вашу роль",
            True,
        )

    def _login(self) -> tuple[LogStr, object | None]:
        """Логин пользователя, с проверкой по БД"""

        executor = USERS.find_one({"login": self.login})

        if not executor:
            return "Пользователь с таким логином не зарегистрирован!", None

        if not check_password_hash(executor["password"], self.password):
            return "Неверный пароль!", None

        if not executor["role"]:
            return "У вас нет роли! Обратитесь к администратору", None

        Role = ROLES_NAMES[executor["role"]]
        return "Вход успешен!", Role(self.login, self.password)


class Worker(User):
    """Офисный работник"""

    def _make_order(self, is_delivery, address, dishes: list[dict]) -> LogStr:
        """Оформление заказа пользователем"""

        date = dt.combine(d.today(), dt.min.time())
        summaty_cost = 0
        for dish in dishes:
            summaty_cost += dish["price"] * dish["quantity"]
        ORDERS.insert_one(
            {
                "user_login": self.login,
                "dishes": dishes,
                "status": "В обработке",
                "cost": summaty_cost,
                "date": date,
                "deliverier": None,
                "is_delivery": is_delivery,
                "address": address,
            }
        )
        return "Заказ успешно оформлен!"


class Deliverier(User):
    """Курьер, получает заказы направленные на него, изменяет статус на доставлен"""

    def _set_order_status(self, order_id: str, order_status: str) -> str:
        """Устанавливает заказу следующий по циклу статус"""
        q = {"_id": ObjectId(order_id)}

        ORDERS.update_one(q, {"$set": {"status": order_status}})
        return order_status


class Manager(User):
    """Администратор офиса, который может добавлять и удалять работников из офиса

    Как и Worker может сделать заказ"""

    def _make_order(self, is_delivery, address, dishes: list[dict]) -> LogStr:
        """Оформление заказа пользователем"""

        date = dt.combine(d.today(), dt.min.time())
        summaty_cost = 0

        for dish in dishes:
            summaty_cost += dish["price"] * dish["quantity"]
        ORDERS.insert_one(
            {
                "user_login": self.login,
                "dishes": dishes,
                "status": "В обработке",
                "cost": summaty_cost,
                "date": date,
                "deliverier": None,
                "is_delivery": is_delivery,
                "address": address,
            }
        )
        return "Заказ успешно оформлен!"

    def _add_worker(self, user_login: str) -> LogStr:
        """Устанавливает юзеру роль worker

        C фронта user_login только юзеры без роли)"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Пользователь не найден!"

        USERS.update_one(q, {"$set": {"role": "worker", "parent": self.login}})

        return "Роль успешно выдана!"

    def _remove_worker(self, user_login: str) -> LogStr:
        """Увольняет пользователя

        С фронта user_login только подчиненных"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        USERS.delete_one(q)

        return "Сотрудник успешно удален!"


class Cooker(User):
    """Админ кафе добавляет блюда, составляет меню,
    Получает заказы и распределяет их по курьерам, устанавливает статусы заказов"""

    def _add_deliverier(self, user_login):
        """Устанавливает юзеру роль deliverier

        C фронта user_login только юзеры без роли)"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Пользователь не найден!"

        USERS.update_one(q, {"$set": {"role": "deliverier", "parent": self.login}})
        return "Роль успешно выдана!"

    def _remove_deliverier(self, user_login: str) -> LogStr:
        """Увольняет пользователя

        С фронта user_login только подчиненных"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        USERS.delete_one(q)

        return "Сотрудник успешно удален!"

    def _give_order(self, order_id: str, user_login: str) -> LogStr:
        """Назначает заказ на курьера

        С фронта user_login только подчиненных"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        ORDERS.update_one(
            {"_id": ObjectId(order_id)}, {"$set": {"deliverier": user_login}}
        )

        return "Заказ успешно назначен!"

    def _set_order_status(self, order_id: str, order_status: str) -> str:
        """Устанавливает заказу следующий по циклу статус"""
        q = {"_id": ObjectId(order_id)}

        ORDERS.update_one(q, {"$set": {"status": order_status}})
        return order_status

    def _add_dish(self, title, structure, photo, cost) -> LogStr:
        """Добавляет блюдо в меню"""

        if DISHES.find_one({"title": title}):
            return "Блюдо с таким названием уже есть!"

        photoname = title + "." + photo.filename.split(".")[-1]
        photo_id = FILES.put(photo, filename=photoname)
        f = FILES.find_one({"filename": photoname})
        if not f:
            return "Фотография блюда не загрузилась в бд!"

        photob64 = b64encode(BytesIO(f.read()).getvalue()).decode()

        DISHES.insert_one(
            {
                "title": title,
                "structure": structure,
                "photo": photob64,
                "photo_id": photo_id,
                "cost": cost,
                "scores": {"sum": 0, "len": 0},
            }
        )
        return "Блюдо успешно добавлено"

    def _edit_dish(self, old_title, title, structure, photo, cost) -> LogStr:
        q = {"title": old_title}

        old_dish = DISHES.find_one(q)

        if not old_dish:
            return f"Блюдо {old_title} не существует!"

        if DISHES.find_one({"title": title}) and not title == old_title:
            return "Блюдо с таким названием уже есть!"

        if photo:
            FILES.delete(old_dish["photo_id"])

            photoname = title + "." + photo.filename.split(".")[-1]
            photo_id = FILES.put(photo, filename=photoname)
            f = FILES.find_one({"filename": photoname})
            if not f:
                return "Фотография блюда не загрузилась в бд!"

            photob64 = b64encode(BytesIO(f.read()).getvalue()).decode()
        else:
            photo_id = old_dish["photo_id"]
            photob64 = old_dish["photo"]

        DISHES.update_one(
            q,
            {
                "$set": {
                    "title": title,
                    "structure": structure,
                    "photo": photob64,
                    "photo_id": photo_id,
                    "cost": cost,
                }
            },
        )
        return "Блюдо усмпешно отредактировано!"

    def _remove_dish(self, title: str) -> None:
        """Удаляет блюдо из меню"""

        DISHES.delete_one({"title": title})


class Admin(User):
    """Самый высокий в иерархии управляет Manager и Cooker"""

    def _add_manager(self, user_login: str) -> LogStr:
        """Устанавливает роль manager юзеру

        C фронта user_login только юзеры без роли
        """

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Пользователь не найден!"

        USERS.update_one(q, {"$set": {"role": "manager", "parent": self.login}})

        return "Роль успешно выдана!"

    def _remove_manager(self, user_login: str) -> LogStr:
        """Увольняет менеджера, убирает роль его подчиенным

        С фронта user_login только подчиненных"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        USERS.delete_one(q)

        return "Сотрудник успешно уволен!"

    def _change_cooker(self, user_login: str) -> LogStr:
        """Заменяет/Устанавливает нового кукера

        C фронта user_login только юзеры без роли
        """

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Пользователь не найден!"

        USERS.delete_one({"role": "cooker"})
        USERS.update_one(q, {"$set": {"role": "cooker", "parent": self.login}})

        return "Новый кукер успешно установлен!"


ROLES_NAMES = {
    cls.__name__.lower(): cls
    for cls in (User, Worker, Deliverier, Manager, Cooker, Admin)
}
