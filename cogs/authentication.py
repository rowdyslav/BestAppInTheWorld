from typing import Optional
from db_connector import USERS

# pyright: reportOptionalSubscript=false


def _registration(
    email: str, password: str, fio: str
) -> tuple[str, bool, Optional[str]]:
    ctx_user = USERS.find_one({"email": email})
    if ctx_user:
        return "Пользователь уже зарегистрирован!", False, None

    USERS.insert_one({"email": email, "password": password, "fio": fio, "role": "user"})
    return "Регистрация успешна!", True, "user"


def _login(email: str, password: str) -> tuple[str, bool, Optional[str]]:
    ctx_user = USERS.find_one({"email": email})
    role = ctx_user["role"]
    if not ctx_user:
        return "Пользователь с таким email не зарегистрирован!", False, None

    if ctx_user["password"] != password:
        return "Неверный пароль!", False, None

    return "Вход успешен!", True, role
