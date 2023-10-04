from db_connector import USERS, OFFICES


def add_office(
    cooker,
    admin_email,
    name="Имя оффиса по умолчанию",
    address="Адрес оффиса по умолчанию",
) -> None:
    OFFICES.insert_one(
        {
            "name": name,
            "manager_email": admin_email,
            "address": address,
            "workers_emails": [],
        }
    )


def remove_office(cooker, office_name) -> None:
    OFFICES.find_one_and_delete({"name": office_name})
