from flask import Flask, render_template, redirect, url_for, request, session
from flask_session import Session

from cogs.authentication import registration, login
from cogs.utils import login_required

from db_connector import USERS, OFFICES


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
    result = registration(email, password, fio)
    if result[1]:
        session["email"] = email
        return redirect(url_for("account", email=email))
    else:
        return render_template("index.html", error_msg=result[0])


@app.route("/log", methods=["POST"])
def log():
    email = request.form["loginEmail"]
    password = request.form["loginPassword"]
    result = login(email, password)
    if result[1]:
        session["email"] = email
        if result[2] == 'user':
            return redirect(url_for('account', email=email))
        elif result[2] == 'admin':
            return redirect(url_for('admin_account', email=email))
        elif result[2] == 'cooker':
            return redirect(url_for('cooker_account', email=email))
    else:
        return render_template('index.html', error_msg=result[0])


@app.route("/account")
@login_required
def account():
    email = request.args.get("email")
    user = USERS.find_one({"email": email})
    return render_template("user_account.html", user=user)


@app.route("/exit")
def exit():
    session.pop('email', None)
    return redirect(url_for("index", error_msg=None))


@app.route("/admin_account")
@login_required
def admin_account():
    email = request.args.get("email")
    admin = USERS.find_one({"email": email})
    address = OFFICES.find_one({'manager_email': email})['address']
    return render_template("admin_account.html", admin=admin, address=address)


@app.route("/cooker_account")
@login_required
def cooker_account():
    email = request.args.get("email")
    cooker = USERS.find_one({"email": email})
    return render_template("cooker_account.html", cooker=cooker)


if __name__ == "__main__":
    app.run(debug=True)
