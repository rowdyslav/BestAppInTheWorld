from flask import Flask
from roles import User
from db import USERS
from pprint import pprint


def main():
    print("HelloWorld!")
    a = USERS.find_one({"login": "admin"})
    pprint(a)


if __name__ == "__main__":
    main()
