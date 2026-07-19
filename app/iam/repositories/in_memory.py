from typing import Optional, List

from .base import UserRepository
from ..schema_user_profile import UserProfile


class InMemoryUserRepository(UserRepository):
    def __init__(self):
        self._users: dict[str, UserProfile] = {}

    def save(self, user: UserProfile) -> None:
        self._users[user.user_id] = user

    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        return self._users.get(user_id)

    def get_all(self) -> List[UserProfile]:
        return list(self._users.values())

    def update(self, user: UserProfile) -> None:
        self._users[user.user_id] = user

    def exists_by_email(self, email: str) -> bool:
        return any(u.email == email for u in self._users.values())
