from roles import User
from sys import argv

fields = ["Логин", "Пароль", "ФИО"]
cmd_args = {x[0]: x[1] for x in enumerate(argv)}

data = []
for i, field in enumerate(fields, 1):
    value = cmd_args.get(i)
    if value:
        print(f"{field} нового кукера > {value}")
    else:
        value = input(f"{field} нового кукера > ")
    data.append(value)

login, password, fio = data
print(User(login, password, fio)._registration("cooker"))
