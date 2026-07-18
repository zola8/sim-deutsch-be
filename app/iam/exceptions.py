class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"User {field} already exists")


class UserNotFoundError(Exception):
    pass
