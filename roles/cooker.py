from db_connector import USERS, OFFICES
from roles.base import Base


class Cooker(Base):
    def _add_office(
        self, admin_login, admin_password, admin_fio, office_name, office_address
    ) -> None:
        """Добавляет виртуальную учетку админа и связанный с ним оффис в бд"""

        USERS.insert_one(
            {
                "login": admin_login,
                "password": admin_password,
                "fio": admin_fio,
                "role": "admin",
            }
        )

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
