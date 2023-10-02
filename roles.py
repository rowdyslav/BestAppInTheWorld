class Role:
    def __init__(self, fio) -> None:
        self.fio = fio

    def __str__(self) -> str:
        return self.fio

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{vars(self)}"


class User(Role):
    pass


class Admin(User):
    pass


class Cooker(Role):
    pass
