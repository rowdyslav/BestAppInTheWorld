from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from typing import Literal

from roles import User
from roles import Worker
from roles import Manager
from roles import Cooker
from roles import Deliverier
from roles import Admin

from datetime import date as d
from datetime import datetime as dt

from utils import _role_required

from db_conn import USERS, ORDERS, DISHES

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

TABLES = 15


@app.route("/")
def index():
    status = session.get("status")
    session.pop("status", None)
    user = session.get("user")

    return render_template("index.html", status=status, user=user)


@app.route("/reg", methods=["POST"])
def reg():
    login = request.form["regLogin"]
    password = request.form["regPassword"]
    fio = request.form["regFio"]

    reg_user = User(login, password)
    reg_result = reg_user._registration(fio)
    session["status"] = reg_result
    return redirect("/")


@app.route("/log", methods=["POST"])
def log():
    login = request.form["logLogin"]
    password = request.form["logPassword"]
    log_user = User(login, password)
    log_result = log_user._login()
    if log_result[1]:
        session["user"] = log_result[1]
        return redirect(url_for("account"))
    else:
        session["status"] = log_result[0]
        return redirect("/")


@app.route("/account")
def account():
    user = session["user"]
    match user:
        case Worker():
            worker = USERS.find_one({"login": session["user"].login})
            dishes = list(DISHES.find({}))
            date = dt.combine(d.today(), dt.min.time())
            busy = f"{(len(list(ORDERS.find({"date": date}))) / TABLES) * 100}%"

            context = {"worker": worker, "dishes": dishes, "busy": busy}

        case Deliverier():
            deliverier = USERS.find_one({"login": session["user"].login})

            context = {"deliverier": deliverier}

        case Cooker():
            cooker = USERS.find_one({"login": session["user"].login})
            dishes = list(DISHES.find({}))

            context = {"cooker": cooker, "dishes": dishes}

        case Manager():
            manager = USERS.find_one({"login": session["user"].login})
            meals = session["user"]._get_meals_order()
            users = list(USERS.find({"role": None}))

            context = {
                "manager": manager,
                "meals": meals,
                "users": users,
            }

        case Admin():
            admin = USERS.find_one({"login": session["user"].login})
            users = list(USERS.find({"role": None}))

            context = {
                "admin": admin,
                "users": users,
            }

        case _:
            return "Ошибка! Неизвестная роль!"
    return render_template(f"{user.__class__.__name__.lower()}_account.html", **context)


@app.route("/exit")
@_role_required(User)
def exit():
    session.pop("user", None)
    return redirect("/")


@app.route("/send_meals", methods=["POST"])
@_role_required(Worker)
def send_meals():
    executor: Worker = session["user"]

    meals: dict[
        Literal["brejakfast", "dinner"], bool
    ] = NotImplemented  # надо будет получать с фронта данные о двух галочках

    executor._send_meals(meals)
    return redirect(url_for("account"))


@app.route("/add_worker", methods=["POST"])
@_role_required(Manager)
def add_worker():
    executor: Manager = session["user"]

    worker_login = request.form["workerLoginForAdd"]
    executor._add_worker(worker_login)
    return redirect(url_for("account"))


@app.route("/remove_worker", methods=["POST"])
@_role_required(Manager)
def remove_worker():
    executor: Manager = session["user"]

    worker_login = request.form["workerLoginForRemove"]
    executor._remove_worker(worker_login)
    return redirect(url_for("account"))


@app.route("/send_meals_order", methods=["POST"])
@_role_required(Manager)
def send_meals_order():
    executor: Manager = session["user"]

    # executor._send_meals_order()
    return redirect(url_for("account"))


@app.route("/add_dish", methods=["POST"])
@_role_required(Cooker)
def add_dish():
    executor: Cooker = session["user"]

    dish_title = request.form["dishTitle"]
    dish_structure = request.form["dishStructure"]
    dish_image = request.files["dishImage"]
    dish_cost = int(request.form["dishCost"])

    executor._add_dish(dish_title, dish_structure, dish_image, dish_cost)
    return redirect(url_for("account"))

@app.route("/set_role", methods=["POST"])
@_role_required(Admin)
def set_role():
    executor: Admin = session['user']

    user_login = request.form["userLoginForSet"]
    role = request.form["roleSelect"]

    executor._set_role(user_login, role)
    return redirect(url_for("account"))

if __name__ == "__main__":
    app.run(debug=True)
