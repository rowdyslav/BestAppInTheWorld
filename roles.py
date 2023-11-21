from dataclasses import dataclass
from typing import Literal

from io import BytesIO
import base64

from werkzeug.security import generate_password_hash, check_password_hash

from db_conn import USERS, OFFICES, DISHES, FILES, ORDERS
from utils import _is_login_free

from datetime import date as dt

type Result = str
type Success = bool


@dataclass
class User:
    """Базовый класс для всех ролей"""

    login: str
    password: str

    def _registration(self, fio) -> Result:
        """Регистрация нового пользователя с ролью role"""

        if not _is_login_free(self.login):
            return "Логин уже занят!"

        self.password = generate_password_hash(self.password)
        USERS.insert_one(
            {
                "login": self.login,
                "password": self.password,
                "fio": fio,
                "role": None,
                "parent": None,
            }
        )

        return "Регистрация успешна! Теперь администратор должен назначить вашу роль"

    def _login(self) -> tuple[Result, object | None]:
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
    """офисный работник, который отмечает себе питание методом _send_meals"""

    def _send_meals(self, meals: list) -> None:
        """Отправка заказа пользователем
        meals:list(dishes_id)"""
        date = dt.today()
        summaty_cost = 0
        for meal_title in meals:
            summaty_cost += DISHES.find_one({"title": meal_title})["cost"]  # type: ignore
        ORDERS.insert_one(
            {
                "user_login": self.login,
                "meals": meals,
                "status": "В обработке",
                "cost": summaty_cost,
                "date": date,
            }
        )


class Deliverier(User):
    """Курьер, получает заказы направленные на него, изменяет статус на доставлен"""

    def _send_order_complite(self):
        """делает заказ 'завершённым'"""
        ...


class Manager(User):
    """Администратор офиса, который может добавлять и удалять работников из офиса, а также отправляет итоговый заказ _send_meals_order"""

    def _add_worker(self, worker_login: str) -> Result:
        """Добавляет работника в свой офис"""

        q = {"login": worker_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        USERS.update_one(q, {"$set": {"role": "worker", "parent": self.login}})

        return "Роль успешно выдана!"

    def _remove_worker(self, worker_login: str) -> Result:
        """Удаляет работника из своего офиса"""

        q = {"login": worker_login, "role": "worker"}

        worker = USERS.find_one()
        if not worker:
            return "Сотрудник не найден!"

        USERS.update_one(q, {"$set": {"role": "user"}})
        return "Сотрудник успешно удален из вашего офиса!"

    # Надо полностью переписать
    def _get_meals_order(self):
        """Получить итоговый заказ со всего офиса"""

        office = OFFICES.find_one({"admin_login": self.login})
        if not office:
            return "Ошибка! Офис не найден, возможно он был удален."

        workers = office["workers_logins"]
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


class Cooker(User):
    """Админ кафе добавляет блюда, составляет меню, получает заказы"""

    def _add_dish(self, title, structure, photo, cost) -> Result:
        """Функция добавляет блюдо в меню офиса"""

        if DISHES.find_one({"title": title}):
            return "Блюдо с таким названием уже есть!"

        photoname = title + "." + photo.filename.split(".")[-1]
        FILES.put(photo, filename=photoname)
        f = FILES.find_one({"filename": photoname})

        photob64 = base64.b64encode(BytesIO(f.read()).getvalue()).decode()  # type: ignore
        DISHES.insert_one(
            {
                "title": title,
                "structure": structure,
                "photo": photob64,
                "cost": cost,
            }
        )
        return "Блюдо успешно добавлено"

    """Получает заказы и распределяет их по курьерам и устанавливает статус"""

    def _get_orders(self):
        """Получает все заказы
        Выводит в виде суммы продуктов и/или заказов по отдельности"""
        work_date = dt.today()
        orders = ORDERS.find({"date": work_date})
        if not orders:
            return f"Нет заказов на дату{work_date}", False
        else:
            ...

    def _change_order_status(self, order_id):
        """Меняет статус заказа (В обработке, Готов к получению, Доставлен)"""
        ...

    # ПОЛНОСТЬЮ НАПИСАТЬ
    def _create_menu(self):
        """cocтавление меню на неделю"""
        ...


class Admin(User):
    """Самый высокий в иерархии управляет Manager и Cooker"""

    def _set_role(self, user_login: str, role: str) -> Result:
        """Добавляет работника в свой офис"""

        q = {"login": user_login}

        user = USERS.find_one(q)
        if not user:
            return "Сотрудник не найден!"

        USERS.update_one(q, {"$set": {"role": role, "parent": self.login}})

        return "Роль успешно выдана!"

    ...


ROLES_NAMES = {
    cls.__name__.lower(): cls
    for cls in (User, Worker, Deliverier, Manager, Cooker, Admin)
}
