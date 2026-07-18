import uuid

from .exceptions import UserAlreadyExistsError, UserNotFoundError
from .schemas import UserCreateRequest, UserCreateResponse, UserStatus, UserProfile


class UserService:
    def __init__(self):
        # TODO dummy in-memory storage
        self._users: dict[str, UserProfile] = {}

    def create_user(self, request: UserCreateRequest) -> UserCreateResponse:
        for existing_user in self._users.values():
            if existing_user.email == request.email:
                raise UserAlreadyExistsError("email")

        new_id = str(uuid.uuid4())

        profile = UserProfile(
            user_id=new_id,
            username=request.username,
            email=request.email,
            password=request.password,
            roles=['USER'],
            # status, created_at will use their default values
        )

        self._users[new_id] = profile

        return UserCreateResponse(user_id=profile.user_id, status=profile.status)

    def get_user(self, user_id: str) -> UserProfile | None:
        return self._users.get(user_id)

    def get_all_users(self) -> list[UserProfile]:
        return list(self._users.values())

    def delete_user(self, user_id: str) -> UserCreateResponse:
        if user_id not in self._users:
            raise UserNotFoundError()

        user = self._users[user_id]
        updated_user = user.model_copy(update={"status": UserStatus.DELETED})
        self._users[user_id] = updated_user

        return UserCreateResponse(user_id=updated_user.user_id, status=updated_user.status)
