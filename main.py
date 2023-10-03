from flask import Flask, render_template, request
from authentication import registration, login

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/reg', methods=['POST'])
def reg():
    fio = request.form['registerFio']
    email = request.form['registerEmail']
    password = request.form['registerPassword']
    result = registration(email, password, fio)
    return result[0]


@app.route('/log', methods=['POST'])
def log():
    email = request.form['loginEmail']
    password = request.form['loginPassword']
    result = login(email, password)
    return result[0]


if __name__ == "__main__":
    app.run(debug=True)
