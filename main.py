from os import error
from flask import Flask, render_template, redirect, url_for, request, session, send_file
from flask_session import Session

from typing import Literal

from roles import Base
from roles import Worker
from roles import Admin
from roles import Cooker

from utils import _role_required

from db_connector import USERS, OFFICES, CUBEFOOD_DB

from io import BytesIO

from gridfs import GridFS



app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    auth_error = session.get("auth_error")

    return render_template("index.html", error_msg=auth_error)


@app.route("/reg", methods=["POST"])
def reg():
    login = request.form["regLogin"]
    password = request.form["regPassword"]
    fio = request.form["regFio"]

    reg_user = Base(login, password, fio)
    reg_result = reg_user._registration("worker")
    if reg_result[1]:
        session["user"] = reg_result[1]
        return redirect(url_for("worker_account"))
    else:
        session["auth_error"] = reg_result[0]
        return redirect("/")


@app.route("/log", methods=["POST"])
def log():
    login = request.form["logLogin"]
    password = request.form["logPassword"]
    log_user = Base(login, password, "")
    log_result = log_user._login()
    if log_result[1]:
        session["user"] = log_result[1]
        return redirect(url_for(f"{log_result[1].__class__.__name__.lower()}_account"))
    else:
        session["auth_error"] = log_result[0]
        return redirect("/")


@app.route("/exit")
@_role_required(Base)
def exit():
    session.pop("user", None)
    return redirect("/")


@app.route("/worker_account")
@_role_required(Worker)
def worker_account():
    worker = USERS.find_one({"login": session["user"].login})
    worker["office"] = OFFICES.find_one({"workers_logins": {"$in": [worker["login"]]}})

    return render_template("worker_account.html", worker=worker)


@app.route("/send_meals", methods=["POST"])
@_role_required(Worker)
def send_meals():
    executor: Worker = session["user"]

    meals: dict[
        Literal["breakfast", "dinner"], bool
    ] = NotImplemented  # надо будет получать с фронта данные о двух галочках

    executor._send_meals(meals)
    return redirect(url_for("worker_account"))


@app.route("/admin_account")
@_role_required(Admin)
def admin_account():
    admin = USERS.find_one({"login": session["user"].login})
    office = OFFICES.find_one({"admin_login": session["user"].login})
    meals = session["user"]._get_meals_order()

    return render_template(
        "admin_account.html", admin=admin, office=office, meals=meals
    )


@app.route("/add_worker", methods=["POST"])
@_role_required(Admin)
def add_worker():
    executor: Admin = session["user"]

    worker_login = request.form["workerLoginForAdd"]
    executor._add_worker(worker_login)
    return redirect(url_for("admin_account"))


@app.route("/remove_worker", methods=["POST"])
@_role_required(Admin)
def remove_worker():
    executor: Admin = session["user"]

    worker_login = request.form["workerLoginForRem"]
    executor._remove_worker(worker_login)
    return redirect(url_for("admin_account"))


@app.route("/add_dish", methods=["POST"])
@_role_required(Admin)
def add_dish():
    executor: Admin = session["user"]

    dish_title = request.form["dishTitle"]
    dish_description = request.form["dishDescription"]
    dish_structure = request.form["dishStructure"]
    dish_image = request.files['dishImage'] # nikola_change
    executor._add_dish(dish_title, dish_description, dish_structure, dish_image)
    return redirect(url_for("admin_account"))



@app.route("/send_meals_order", methods=["POST"])
@_role_required(Admin)
def send_meals_order():
    executor: Admin = session["user"]

    # executor._send_meals_order()
    return redirect(url_for("admin_account"))


@app.route("/cooker_account")
@_role_required(Cooker)
def cooker_account():
    cooker = USERS.find_one({"login": session["user"].login})
    return render_template("cooker_account.html", cooker=cooker)


@app.route("/add_office", methods=["POST"])
@_role_required(Cooker)
def add_office():
    executor: Cooker = session["user"]

    login = request.form["officeLoginForAdd"]
    password = request.form["officePasswordForAdd"]
    fio = request.form["officeFioForAdd"]
    name = request.form["companyNameForAdd"]
    address = request.form["officeAddressForAdd"]

    executor._add_office(login, password, fio, name, address)
    return redirect(url_for("cooker_account"))


@app.route("/remove_office", methods=["POST"])
@_role_required(Cooker)
def remove_office():
    executor: Cooker = session["user"]

    admin_login = request.form["adminLoginForRem"]

    executor._remove_office(admin_login)
    return redirect(url_for("cooker_account"))

@app.route('/image/<filename>')
def get_image(filename):
    fs = GridFS(CUBEFOOD_DB)
    file = fs.find_one({'filename': filename})
    return send_file(BytesIO(file.read()), mimetype='image/jpg')


if __name__ == "__main__":
    app.run(debug=True)
