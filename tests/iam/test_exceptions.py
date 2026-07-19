from app.iam import UserNotFoundError, UserAlreadyExistsError


class TestUserNotFoundError:
    def test_with_user_id(self):
        exc = UserNotFoundError(user_id="abc-123")
        assert exc.user_id == "abc-123"
        assert "abc-123" in exc.message
        assert str(exc) == "User with id 'abc-123' not found"

    def test_without_user_id(self):
        exc = UserNotFoundError()
        assert exc.user_id is None
        assert exc.message == "User not found"


class TestUserAlreadyExistsError:
    def test_with_field(self):
        exc = UserAlreadyExistsError(field="email")
        assert exc.field == "email"
        assert "email" in str(exc)
        assert "already exists" in str(exc)
