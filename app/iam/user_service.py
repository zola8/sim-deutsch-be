import uuid

from .schemas import UserCreateRequest, UserCreateResponse


class UserService:
    def __init__(self):
        # TODO dummy in-memory storage
        self._users: dict[str, UserCreateResponse] = {}

    def create_user(self, user: UserCreateRequest) -> UserCreateResponse:
        _new_id = str(uuid.uuid4())

        new_user = UserCreateResponse(
            id=_new_id,
            username=user.username,
            email=user.email
        )

        self._users[_new_id] = new_user
        return new_user

    def get_user(self, user_id: str) -> UserCreateResponse | None:
        return self._users.get(user_id)

    def get_all_users(self) -> list[UserCreateResponse]:
        return list(self._users.values())
