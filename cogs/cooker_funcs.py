from db_connector import USERS, OFFICES


def _add_office(admin_email, admin_password, admin_fio, office_name, office_address) -> None:
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
            "name": office_name,
            "admin_email": admin_email,
            "address": office_address,
            "workers_emails": [],
        }
    )


def _remove_office(admin_email) -> None:
    USERS.find_one_and_delete({"email": admin_email})
    OFFICES.find_one_and_delete({"admin_email": admin_email})
