from typing import Optional, List

from app.iam.orm.repository_base import UserRepository, CredentialRepository
from app.iam.api.schema_enums import CredentialType
from app.iam.api.schema_user_profile import UserProfile
from app.iam.api.schema_user_profile_credential import UserProfileCredential


class InMemoryUserRepository(UserRepository):
    """In-memory implementation of UserRepository for testing."""

    def __init__(self):
        self._users: dict[str, UserProfile] = {}

    def create_user(self, user: UserProfile) -> UserProfile:
        if user.user_id in self._users:
            raise ValueError(f"User with id {user.user_id} already exists")
        self._users[user.user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    def get_all_users(self) -> List[UserProfile]:
        return list(self._users.values())

    def update_user(self, user: UserProfile) -> UserProfile:
        if user.user_id not in self._users:
            raise ValueError(f"User with id {user.user_id} not found")
        self._users[user.user_id] = user
        return user

    def delete_user(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False


class InMemoryCredentialRepository(CredentialRepository):
    """In-memory implementation of CredentialRepository for testing."""

    def __init__(self):
        self._credentials: dict[int, UserProfileCredential] = {}
        self._next_id = 1

    def create_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        # Assign ID if not provided (simulates database auto-increment)
        if credential.id is None:
            credential.id = self._next_id
            self._next_id += 1

        self._credentials[credential.id] = credential
        return credential

    def get_credential(self, credential_id: int) -> Optional[UserProfileCredential]:
        return self._credentials.get(credential_id)

    def get_credentials_by_user_id(self, user_id: str) -> List[UserProfileCredential]:
        return [cred for cred in self._credentials.values() if cred.user_id == user_id]

    def get_credential_by_type(
        self,
        user_id: str,
        credential_type: CredentialType
    ) -> Optional[UserProfileCredential]:
        for cred in self._credentials.values():
            if cred.user_id == user_id and cred.credential_type == credential_type:
                return cred
        return None

    def update_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        if credential.id not in self._credentials:
            raise ValueError(f"Credential with id {credential.id} not found")
        self._credentials[credential.id] = credential
        return credential

    def delete_credential(self, credential_id: int) -> bool:
        if credential_id in self._credentials:
            del self._credentials[credential_id]
            return True
        return False

    def delete_credentials_by_user_id(self, user_id: str) -> int:
        credentials_to_delete = [
            cred_id for cred_id, cred in self._credentials.items()
            if cred.user_id == user_id
        ]
        for cred_id in credentials_to_delete:
            del self._credentials[cred_id]
        return len(credentials_to_delete)
