# app/iam/repositories/base.py

from abc import ABC, abstractmethod
from typing import Optional, List

from .schema_enums import CredentialType
from .schema_user_profile import UserProfile
from .schema_user_profile_credential import UserProfileCredential


class UserRepository(ABC):
    """Interface for user profile operations."""

    @abstractmethod
    def create_user(self, user: UserProfile) -> UserProfile:
        """Create a new user profile."""
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user by user_id."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user by email address."""
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        """Get user by username."""
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserProfile]:
        """Get all users."""
        pass

    @abstractmethod
    def update_user(self, user: UserProfile) -> UserProfile:
        """Update an existing user profile."""
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete a user by user_id. Returns True if deleted, False if not found."""
        pass


class CredentialRepository(ABC):
    """Interface for user credential operations."""

    @abstractmethod
    def create_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        """Create a new credential."""
        pass

    @abstractmethod
    def get_credential(self, credential_id: int) -> Optional[UserProfileCredential]:
        """Get credential by ID."""
        pass

    @abstractmethod
    def get_credentials_by_user_id(self, user_id: str) -> List[UserProfileCredential]:
        """Get all credentials for a user."""
        pass

    @abstractmethod
    def get_credential_by_type(
        self,
        user_id: str,
        credential_type: CredentialType
    ) -> Optional[UserProfileCredential]:
        """Get a specific credential type for a user."""
        pass

    @abstractmethod
    def update_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        """Update an existing credential."""
        pass

    @abstractmethod
    def delete_credential(self, credential_id: int) -> bool:
        """Delete a credential by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def delete_credentials_by_user_id(self, user_id: str) -> int:
        """Delete all credentials for a user. Returns count of deleted credentials."""
        pass
