class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"User {field} already exists")


class UserNotFoundError(Exception):
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.message = f"User with id {user_id} not found"
        super().__init__(self.message)
