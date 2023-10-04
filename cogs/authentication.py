from db_connector import USERS


def registration(email, password, fio) -> tuple[str, bool]:
    ctx_user = USERS.find_one({"email": email})
    role = ctx_user["role"] = "user"
    if ctx_user:
        return "Пользователь уже зарегистрирован!", False

    USERS.insert_one({"email": email, "password": password, "fio": fio})
    return "Регистрация успешна!", True, role


def login(email: str, password: str) -> tuple[str, bool]:
    ctx_user = USERS.find_one({"email": email})
    role = ctx_user["role"]
    if not ctx_user:
        return "Пользователь с таким email не зарегистрирован!", False

    if ctx_user["password"] != password:
        return "Неверный пароль!", False

    return "Вход успешен!", True, role
