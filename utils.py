import functools

from flask import render_template, session

from db_conn import USERS


def _is_login_free(login: str) -> bool:
    user_with_login = USERS.find_one({"login": login})
    if user_with_login:
        return False
    return True


def _role_required(*roles: type):
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            if all([not isinstance(session.get("user"), role) for role in roles]):
                return render_template("index.html", status="Недостаточно прав!")
            return func(*args, **kwargs)

        return secure_function

    return decorator
