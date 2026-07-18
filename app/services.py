from fastapi import Depends

from iam import (
    UserService, InMemoryUserRepository, UserRepository
)

_dummy_repo = InMemoryUserRepository()


def get_user_repo() -> UserRepository:
    return _dummy_repo


def get_user_service(repo: UserRepository = Depends(get_user_repo)) -> UserService:
    return UserService(user_repo=repo)
