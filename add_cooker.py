from roles import Base

login = input()
password = input()
fio = input()

print(Base(login, password, fio)._registration("cooker"))
