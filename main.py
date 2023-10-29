from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from typing import Literal

from roles import Base
from roles import Worker
from roles import Admin
from roles import Cooker

from utils import _role_required

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

    reg_user = Base(login, password, fio)
    reg_result = reg_user._registration("worker")
    if reg_result[1]:
        session["class"] = reg_result[1]
        return redirect(url_for("worker_account", login=login))
    else:
        return redirect(url_for("index", error_msg=reg_result[0]))


@app.route("/log", methods=["POST"])
def log():
    login = request.form["logLogin"]
    password = request.form["logPassword"]
    log_user = Base(login, password, "")
    log_result = log_user._login()
    if log_result[1]:
        session["class"] = log_result[1]
        return redirect(
            url_for(f"{log_result[1].__class__.__name__.lower()}_account", login=login)
        )
    else:
        return redirect(url_for("index", error_msg=log_result[0]))


@app.route("/exit")
@_role_required(Base)
def exit():
    session.pop("class", None)
    return redirect(url_for("index"))


@app.route("/worker_account")
@_role_required(Worker)
def worker_account():
    login = request.args.get("login")

    worker = USERS.find_one({"login": login})
    return render_template("worker_account.html", worker=worker)


@app.route("/send_meals", methods=["POST"])
@_role_required(Worker)
def add_meals():
    executor: Worker = session["class"]

    meals: dict[
        Literal["breakfast", "dinner"], bool
    ] = NotImplemented  # надо будет получать с фронта данные о двух галочках

    executor._send_meals(meals)
    return redirect(url_for("admin_account", login=session["class"].login))


@app.route("/admin_account")
@_role_required(Admin)
def admin_account():
    login = request.args.get("login")
    admin = USERS.find_one({"login": login})

    address = OFFICES.find_one({"admin_login": login})["address"]
    return render_template("admin_account.html", admin=admin, address=address)


@app.route("/add_worker", methods=["POST"])
@_role_required(Admin)
def add_worker():
    executor: Admin = session["class"]

    worker_login = request.form["workerLoginForAdd"]
    executor._add_worker(worker_login)
    return redirect(url_for("admin_account", login=session["class"].login))


@app.route("/remove_worker", methods=["POST"])
@_role_required(Admin)
def remove_worker():
    executor: Admin = session["class"]

    worker_login = request.form["workerLoginForRem"]
    executor._remove_worker(worker_login)
    return redirect(url_for("admin_account", login=session["class"].login))


@app.route("/cooker_account")
@_role_required(Cooker)
def cooker_account():
    login = request.args.get("login")

    cooker = USERS.find_one({"login": login})
    return render_template("cooker_account.html", cooker=cooker)


@app.route("/add_office", methods=["POST"])
@_role_required(Cooker)
def add_office():
    executor: Cooker = session["class"]

    login = request.form["officeLoginForAdd"]
    password = request.form["officePasswordForAdd"]
    fio = request.form["officeFioForAdd"]
    name = request.form["companyNameForAdd"]
    address = request.form["officeAddressForAdd"]

    executor._add_office(login, password, fio, name, address)
    return redirect(url_for("cooker_account", cooker=session["class"].login))


@app.route("/remove_office", methods=["POST"])
@_role_required(Cooker)
def remove_office():
    executor: Cooker = session["class"]

    admin_login = request.form["adminLoginForRem"]
    executor._remove_office(admin_login)
    return redirect(url_for("cooker_account", cooker=session["class"].login))


if __name__ == "__main__":
    app.run()
