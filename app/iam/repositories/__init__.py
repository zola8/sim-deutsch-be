from .base import UserRepository
from .in_memory import InMemoryUserRepository

__all__ = [
    "UserRepository",
    "InMemoryUserRepository",
]
