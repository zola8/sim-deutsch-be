from abc import ABC, abstractmethod
from typing import Optional, List

from pydantic import EmailStr

from ..schemas import UserProfile


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: UserProfile) -> None: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserProfile]: ...

    @abstractmethod
    def get_all(self) -> List[UserProfile]: ...

    @abstractmethod
    def update(self, user: UserProfile) -> None: ...

    @abstractmethod
    def exists_by_email(self, email: EmailStr) -> bool: ...
