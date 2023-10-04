from db_connector import USERS, OFFICES
from authentication import registration


def add_office(admin_email, admin_password, admin_fio, name, address) -> None:
    registration(admin_email, admin_password, admin_fio)
    USERS.update_one({"email": admin_email}, {"$set": {"role": "admin"}})
    OFFICES.insert_one(
        {
            "name": name,
            "manager_email": admin_email,
            "address": address,
            "workers_emails": [],
        }
    )


def remove_office(manager_email) -> None:
    USERS.find_one_and_delete({"email": manager_email})
    OFFICES.find_one_and_delete({"manager_email": manager_email})
