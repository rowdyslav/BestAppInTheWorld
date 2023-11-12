from roles import Base

login = input("Логин нового кукера > ")
password = input("Пароль нового кукера > ")
fio = input("ФИО нового кукера > ")

print(Base(login, password, fio)._registration("cooker"))
