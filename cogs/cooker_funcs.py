from db_connector import USERS, OFFICES
from cogs.authentication import registration


def _add_office(admin_email, admin_password, admin_fio, name, address) -> None:
    USERS.insert_one(
        {
            "email": admin_email,
            "password": admin_password,
            "fio": admin_fio,
            "role": "admin",
        }
    )

    OFFICES.insert_one(
        {
            "name": name,
            "admin_email": admin_email,
            "address": address,
            "workers_emails": [],
        }
    )


def _remove_office(admin_email) -> None:
    USERS.find_one_and_delete({"email": admin_email})
    OFFICES.find_one_and_delete({"admin_email": admin_email})
