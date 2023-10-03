from flask import Flask, render_template, request
from cogs.authentication import registration, login
from db_connector import USERS

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/reg", methods=["POST"])
def reg():
    email = request.form["registerEmail"]
    password = request.form["registerPassword"]
    fio = request.form["registerFio"]
    result = registration(email, password, fio)
    return result[0]


@app.route("/log", methods=["POST"])
def log():
    email = request.form["loginEmail"]
    password = request.form["loginPassword"]
    result = login(email, password)
    return result[0]


@app.route("/account")
def account():
    return render_template(
        "user_account.html",
        user=USERS.find_one(
            {"email": "вот здесь должна быть переменная с почтой юзера"}
        ),
    )


if __name__ == "__main__":
    app.run(debug=True)
