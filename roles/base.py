from dataclasses import dataclass
from typing import Optional

from db_connector import USERS


@dataclass
class Base:
    """Базовый класс для всех ролей, но по сути является Хендлером,
    тк до аунтификации данных через бд ценности не несет,

    fio: Optional потому что нужна только при регистрации"""

    login: str
    password: str

    fio: Optional[str] = "Фамилия Имя Отчество"

    def _login(self) -> tuple[str, str | None]:
        executor = USERS.find_one({"login": self.login})

        if not executor:
            return "Пользователь с таким логином не зарегистрирован!", None

        if executor["password"] != self.password:
            return "Неверный пароль!", None

        return "Вход успешен!", executor["role"]
