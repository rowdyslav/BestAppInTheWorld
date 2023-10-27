from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from roles.base import Base
from roles.user import User
from roles.admin import Admin
from roles.cooker import Cooker

from utils import _login_required, _check_user_role, _get_class_by_name

from db_connector import USERS, OFFICES


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reg", methods=["POST"])
def reg():
    login = request.form["regLogin"]
    password = request.form["regPassword"]
    fio = request.form["regFio"]

    reg_user = User(login, password, fio)
    result = reg_user._registration()
    if result[1]:
        session["class"] = reg_user
        return redirect(url_for("user_account", login=login))
    else:
        return render_template("index.html", error_msg=result[0])


@app.route("/log", methods=["POST"])
def log():
    login = request.form["logLogin"]
    password = request.form["logPassword"]
    log_user = Base(login, password)
    result = log_user._login()
    if result[1]:
        session["class"] = log_user
        return redirect(url_for(f"{result[1]}_account", login=login))
    else:
        return render_template("index.html", error_msg=result[0])


@app.route("/user_account")
@_login_required
def user_account():
    login = request.args.get("login")
    user = USERS.find_one({"login": login})
    return render_template("user_account.html", user=user)


@app.route("/exit")
@_login_required
def exit():
    session.pop("login", None)
    return redirect(url_for("index"))


@app.route("/admin_account")
@_login_required
def admin_account():
    login = request.args.get("login")
    admin = USERS.find_one({"login": login})

    address = OFFICES.find_one({"admin_login": login})["address"]
    return render_template("admin_account.html", admin=admin, address=address)


@app.route("/cooker_account")
@_login_required
def cooker_account():
    login = request.args.get("login")
    cooker = USERS.find_one({"login": login})
    return render_template("cooker_account.html", cooker=cooker)


@app.route("/add_worker", methods=["POST"])
@_login_required
def add_worker():
    executor: Admin = session["class"]
    if not _check_user_role(executor, Admin):
        return render_template("index.html", error_msg="Недостаточно прав!")

    worker_login = request.form["workerLoginForAdd"]
    executor._add_worker(worker_login)
    return redirect(url_for("admin_account", login=vars(executor)))


@app.route("/remove_worker", methods=["POST"])
@_login_required
def remove_worker():
    executor: Admin = session["class"]
    if not _check_user_role(executor, Admin):
        return render_template("index.html", error_msg="Недостаточно прав!")

    worker_login = request.form["workerLoginForAdd"]
    executor._remove_worker(worker_login)
    return redirect(url_for("admin_account", login=vars(executor)))


@app.route("/add_office", methods=["POST"])
@_login_required
def add_office():
    executor: Cooker = session["class"]
    if not _check_user_role(executor, Cooker):
        return render_template("index.html", error_msg="Недостаточно прав!")

    fio = request.form["officeFioForAdd"]
    login = request.form["officeLoginForAdd"]
    password = request.form["officePasswordForAdd"]
    name = request.form["companyNameForAdd"]
    address = request.form["officeAddressForAdd"]

    executor._add_office(login, password, fio, name, address)
    return redirect(url_for("cooker_account", cooker=vars(executor)))


@app.route("/remove_office", methods=["POST"])
@_login_required
def remove_office():
    executor: Cooker = session["class"]
    if not _check_user_role(executor, Cooker):
        return render_template("index.html", error_msg="Недостаточно прав!")

    admin_login = request.form["adminLoginForDel"]
    executor._remove_office(admin_login)
    return redirect(url_for("cooker_account", cooker=vars(executor)))


if __name__ == "__main__":
    app.run()
