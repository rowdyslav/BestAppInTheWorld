from db_connector import USERS


class Office:
    def __init__(self, user_email: str, address: str) -> None:
        self.admin = USERS.find_one({"email": user_email})
        self.address = address
        self.workers = []
