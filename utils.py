from flask import render_template, session
import functools

from db_conn import USERS

from roles import ROLES_NAMES


def _is_login_free(login: str) -> bool:
    user_with_login = USERS.find_one({"login": login})
    if user_with_login:
        return False
    return True


def _role_required(role: type):
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            if not isinstance(session.get("user"), role):
                return render_template("index.html", status="Недостаточно прав!")
            return func(*args, **kwargs)

        return secure_function

    return decorator


def _set_role(user_login: str, role: str):
    q = {"login": user_login}

    worker = USERS.find_one(q)
    if not worker:
        return "Сотрудник не найден!"
    
    USERS.update_one(q, {"$set": {"role": role}})

    return "Роль успешно выдана!"