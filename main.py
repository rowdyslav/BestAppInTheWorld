from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from cogs.authentication import registration, login
from cogs.utils import login_required

from db_connector import USERS


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reg", methods=["POST"])
def reg():
    email = request.form["registerEmail"]
    password = request.form["registerPassword"]
    fio = request.form["registerFio"]
    result = registration(email, password, fio)
    if result[1]:
        session["email"] = email
        return redirect(url_for("account", email=email))
    else:
        return result[0]


@app.route("/log", methods=["POST"])
def log():
    email = request.form["loginEmail"]
    password = request.form["loginPassword"]
    result = login(email, password)
    if result[1]:
        session["email"] = email
        return redirect(url_for("account", email=email))
    else:
        return result[0]


@app.route("/account")
@login_required
def account():
    email = request.args.get("email")
    user = USERS.find_one({"email": email})
    return render_template("user_account.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)
