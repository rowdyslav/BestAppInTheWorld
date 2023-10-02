from flask import Flask
from roles import User
from db import USERS
from pprint import pprint
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('templates/main.html')


app.run()
