from flask import render_template, session
import functools

from db_connector import USERS


def _is_login_free(login) -> bool:
    user_with_login = USERS.find_one({"login": login})
    if user_with_login:
        return False
    return True


def _role_required(role):
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            if not isinstance(session.get("user"), role):
                return render_template("index.html", error_msg="Недостаточно прав!")
            return func(*args, **kwargs)

        return secure_function

    return decorator
