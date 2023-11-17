from dataclasses import dataclass
from typing import Literal

from werkzeug.security import generate_password_hash, check_password_hash

from db_conn import USERS, OFFICES, DISHES, FILES, ORDERS
from utils import _is_login_free

type Result = str
type Success = bool


@dataclass
class User:
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


class Worker(User):
    """офисный работник, который отмечает себе питание методом _send_meals"""

    def _send_meals(self, meals: list) -> None:
        """Отправка заказа пользователем
        meals:list(dishes_id)"""
        summaty_cost = 0
        for meal_title in meals:
            summaty_cost += DISHES.find_one({"title":meal_title})['cost']
        ORDERS.insert_one(
            {
                "user_login": self.login,
                "content": meals,
                "status": "В обработке",
                "create_at": self.fio,
                "cost":summaty_cost,
                
            }
        )
        print(meals)

class Admin(User):
    """Администратор офиса, который может добавлять и удалять работников из офиса, а также отправляет итоговый заказ _send_meals_order"""

    def _add_worker(self, worker_login: str) -> Result:
        """Добавляет работника в свой офис"""

        worker = USERS.find_one({"login": worker_login})
        if not worker or worker["role_name"] != "worker":
            return "Сотрудник не найден!"

        office = OFFICES.find_one({"admin_login": self.login})
        if not office:
            return "Ошибка! Офис не найден, возможно он был удален."

        OFFICES.update_one(
            {"_id": office["_id"]}, {"$push": {"workers_logins": worker["login"]}}
        )
        return "Сотрудник успешно добавлен в ваш офис!"

    def _remove_worker(self, worker_login: str) -> Result:
        """Удаляет работника из своего офиса"""

        worker = USERS.find_one({"login": worker_login})
        office = OFFICES.find_one({"admin_login": self.login})
        if not office:
            return "Ошибка! Офис не найден, возможно он был удален."

        if (
            not worker
            or worker["role_name"] != "worker"
            or worker["login"] not in office["workers_logins"]
        ):
            return "Сотрудник не найден или работает не в вашем офисе!"
        OFFICES.update_one(
            {"admin_login": self.login},
            {"$pull": {"workers_logins": worker["login"]}},
        )
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
    """Администратор ресторана, добавляет офисы для обслуживания, вместе с виртуальными учетками их админов"""

    def _add_office(
        self,
        admin_login: str,
        admin_password: str,
        admin_fio: str,
        office_name: str,
        office_address: str,
    ) -> None:
        """Добавляет виртуальную учетку админа и связанный с ним офис в бд"""

        User(admin_login, admin_password, admin_fio)._registration("admin")

        OFFICES.insert_one(
            {
                "name": office_name,
                "admin_login": admin_login,
                "address": office_address,
                "workers_logins": [],
            }
        )

    def _remove_office(self, admin_login) -> None:
        """Удаляет виртуальную учетку админа и связанный с ним офис из бд"""
        USERS.find_one_and_delete({"login": admin_login})
        OFFICES.find_one_and_delete({"admin_login": admin_login})

class Zipper(User):
    """Получает заказы и распределяет их по курьерам и устанавливает статус"""

    def _get_order(self):
        """Получает все заказы
        Выводит в виде суммы продуктов и/или заказов по отдельности"""
        pass

    def _change_order_status(self, order_id):
        """Меняет статус заказа (В обработке, Готов к получению, Доставлен)"""
        pass

class Abc(User):
    """Админ кафе добавляет блюда, составляет меню, получает заказы"""

    def _add_dish(self, title, description, structure, photo, cost) -> Result:
        """Функция добавляет блюдо в меню офиса"""

        office = OFFICES.find_one({"admin_login": self.login})
        if not office:
            return "Ошибка! Офис не найден, возможно он был удален."

        if DISHES.find_one({"title": title}):
            return "Блюдо с таким названием уже есть!"
        else:
            photoname = title + "." + photo.filename.split(".")[-1]
            FILES.put(photo, filename=photoname)
            DISHES.insert_one(
                {
                    "title": title,
                    "description": description,
                    "office": office["_id"],
                    "structure": structure,
                    "photo": photoname,
                    "cost": cost
                }
            )
            return "Блюдо успешно добавлено"
    # ПОЛНОСТЬЮ НАПИСАТЬ
    def _create_menu(self):
        """cocтавление меню на неделю"""
        pass


ROLES_NAMES = {i.__name__.lower(): i for i in (Worker, Admin, Cooker)}
