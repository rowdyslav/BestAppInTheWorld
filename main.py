from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from cogs.authentication import _registration, _login

from cogs.utils import _login_required
from cogs.admin_funcs import _add_worker, _remove_worker
from cogs.cooker_funcs import _add_office, _remove_office

from db_connector import DB_CLIENT, USERS, OFFICES


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html", error_msg=None)


@app.route("/reg", methods=["POST"])
def reg():
    email = request.form["registerEmail"]
    password = request.form["registerPassword"]
    fio = request.form["registerFio"]
    result = _registration(email, password, fio)
    if result[1]:
        session["email"] = email
        return redirect(url_for("user_account", email=email))
    else:
        return render_template("index.html", error_msg=result[0])


@app.route("/log", methods=["POST"])
def log():
    email = request.form["loginEmail"]
    password = request.form["loginPassword"]
    result = _login(email, password)
    if result[1]:
        session["email"] = email
        return redirect(url_for(f"{result[2]}_account", email=email))
    else:
        return render_template("index.html", error_msg=result[0])


@app.route("/user_account")
@_login_required
def user_account():
    email = request.args.get("email")
    user = USERS.find_one({"email": email})
    return render_template("user_account.html", user=user)


@app.route("/exit")
def exit():
    session.pop("email", None)
    return redirect(url_for("index"))


@app.route("/admin_account")
@_login_required
def admin_account():
    email = request.args.get("email")
    admin = USERS.find_one({"email": email})
    address = OFFICES.find_one({"admin_email": email})["address"]
    return render_template("admin_account.html", admin=admin, address=address)


@app.route("/cooker_account")
@_login_required
def cooker_account():
    email = request.args.get("email")
    cooker = USERS.find_one({"email": email})
    return render_template("cooker_account.html", cooker=cooker)


@app.route("/add_worker", methods=["POST"])
def add_worker():
    user_email = request.form["workerEmailForAdd"]
    admin = USERS.find_one({"email": session["email"]})
    _add_worker(admin, user_email)
    return redirect(url_for("admin_account", email=admin["email"]))


@app.route("/remove_worker", methods=["POST"])
def remove_worker():
    user_email = request.form["workerEmailForAdd"]
    admin = USERS.find_one({"email": session["email"]})
    _remove_worker(admin, user_email)
    return redirect(url_for("admin_account", email=admin["email"]))


@app.route("/add_office", methods=["POST"])
def add_office():
    cooker = USERS.find_one({"role": "cooker"})
    fio = request.form["officeFioForAdd"]
    email = request.form["officeEmailForAdd"]
    password = request.form["officePasswordForAdd"]
    name = request.form["companyNameForAdd"]
    address = request.form["officeAddressForAdd"]
    _add_office(email, password, fio, name, address)
    return redirect(url_for("cooker_account", cooker=cooker))


@app.route("/remove_office", methods=["POST"])
def remove_office():
    cooker = USERS.find_one({"email": session["email"]})
    print(cooker)
    email = request.form["adminEmailForDel"]
    _remove_office(email)
    return redirect(url_for("cooker_account", cooker=cooker))


if __name__ == "__main__":
    app.run()
