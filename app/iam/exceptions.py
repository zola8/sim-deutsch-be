class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        self.message = f"User {field} already exists"
        super().__init__(self.message)


class UserNotFoundError(Exception):
    def __init__(self, user_id: str | None = None):
        self.user_id = user_id
        self.message = f"User with id '{user_id}' not found" if user_id else "User not found"
        super().__init__(self.message)


class AuthenticationError(Exception):
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)
