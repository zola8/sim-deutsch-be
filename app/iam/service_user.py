# app/iam/user_service.py

import logging
import uuid
from typing import List, Optional

from .exceptions import UserNotFoundError, UserAlreadyExistsError
from .repository_base import UserRepository
from .schema_user_management import UserCreateRequest, UserUpdateRequest
from .schema_user_profile import UserProfile, UserStatus

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user identity (UserProfile)."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def create_user(self, request: UserCreateRequest) -> UserProfile:
        """
        Create a new user profile.
        Raises UserAlreadyExistsError if email or username is taken.
        """
        # Check for existing email
        if self.user_repo.get_user_by_email(request.email):
            logger.warning(f"Attempted to create user with existing email: {request.email}")
            raise UserAlreadyExistsError(field="email")

        # Check for existing username
        if self.user_repo.get_user_by_username(request.username):
            logger.warning(f"Attempted to create user with existing username: {request.username}")
            raise UserAlreadyExistsError(field="username")

        # Create user profile
        user = UserProfile(
            user_id=str(uuid.uuid4()),
            username=request.username,
            email=request.email,
            status=UserStatus.INACTIVE,
            roles=request.roles if request.roles else ["USER"]
        )

        created_user = self.user_repo.create_user(user)
        logger.info(f"Created user: {created_user.user_id}")
        return created_user

    def get_user(self, user_id: str) -> UserProfile:
        """
        Get user by ID.
        Raises UserNotFoundError if not found.
        """
        user = self.user_repo.get_user(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise UserNotFoundError(user_id=user_id)
        return user

    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email. Returns None if not found."""
        return self.user_repo.get_user_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user by username. Returns None if not found."""
        return self.user_repo.get_user_by_username(username)

    def get_all_users(self) -> List[UserProfile]:
        """Get all users."""
        return self.user_repo.get_all_users()

    def update_user(self, user_id: str, request: UserUpdateRequest) -> UserProfile:
        """
        Update user profile.
        Raises UserNotFoundError if user doesn't exist.
        """
        user = self.get_user(user_id)  # Raises if not found

        # Update fields if provided
        if request.username is not None:
            # Check if new username is taken by another user
            existing = self.user_repo.get_user_by_username(request.username)
            if existing and existing.user_id != user_id:
                raise UserAlreadyExistsError(field="username")
            user.username = request.username

        if request.status is not None:
            user.status = request.status

        if request.roles is not None:
            user.roles = request.roles

        updated_user = self.user_repo.update_user(user)
        logger.info(f"Updated user: {user_id}")
        return updated_user

    def delete_user(self, user_id: str) -> bool:
        """
        Delete user by ID.
        Returns True if deleted, False if not found.
        """
        user = self.user_repo.get_user(user_id)
        if not user:
            logger.warning(f"Attempted to delete non-existent user: {user_id}")
            return False

        result = self.user_repo.delete_user(user_id)
        if result:
            logger.info(f"Deleted user: {user_id}")
        return result
