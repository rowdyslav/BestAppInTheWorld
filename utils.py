from flask import redirect, url_for, session
import functools

from db_connector import USERS


def _get_class_by_name(name: str):
    from roles.user import User
    from roles.admin import Admin
    from roles.cooker import Cooker

    CLASSES_NAMES = {i.__name__.lower(): i for i in (User, Admin, Cooker)}
    return CLASSES_NAMES.get(name)


def _check_user_role(user, role):
    return isinstance(user, role)


def _is_login_free(login) -> bool:
    user_with_login = USERS.find_one({"login": login})
    if user_with_login:
        return False
    return True


def _login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get("class"):
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return secure_function
