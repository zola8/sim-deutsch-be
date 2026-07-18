import uuid

from .exceptions import UserAlreadyExistsError, UserNotFoundError
from .repositories import UserRepository
from .schemas import UserCreateRequest, UserCreateResponse, UserStatus, UserProfile, UserUpdateRequest

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, request: UserCreateRequest) -> UserCreateResponse:
        if self.user_repo.exists_by_email(request.email):
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

        self.user_repo.save(profile)

        return UserCreateResponse(user_id=profile.user_id, status=profile.status)

    def get_user(self, user_id: str) -> UserProfile | None:
        # TODO rights?
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def get_all_users(self) -> list[UserProfile]:
        # TODO rights?
        return self.user_repo.get_all()

    def update_user(self, user_id: str, request: UserUpdateRequest) -> UserProfile:
        # TODO rights?
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        updated_user = user.model_copy(update={
            "username": request.username,
            "status": request.status
        })

        self.user_repo.update(updated_user)
        return updated_user

    def delete_user(self, user_id: str) -> UserCreateResponse:
        # TODO rights?
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        updated_user = user.model_copy(update={"status": UserStatus.DELETED})

        self.user_repo.update(updated_user)

        return UserCreateResponse(user_id=updated_user.user_id, status=updated_user.status)
