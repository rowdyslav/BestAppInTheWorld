from flask import redirect, url_for, session
import functools


def _login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get("email"):
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    return secure_function
