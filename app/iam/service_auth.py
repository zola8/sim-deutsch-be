import logging
import uuid
from datetime import datetime, timezone

from app.core.security import PasswordHasher
from .exceptions import UserNotFoundError, AuthenticationError, UserAlreadyExistsError
from .repository_base import UserRepository, CredentialRepository
from .schema_authentication import RegisterWithPasswordRequest, LoginWithPasswordRequest
from .schema_enums import CredentialType
from .schema_user_profile import UserProfile, UserStatus
from .schema_user_profile_credential import UserProfileCredential

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication (password, OAuth)."""

    def __init__(
        self,
        user_repo: UserRepository,
        credential_repo: CredentialRepository,
        password_hasher: PasswordHasher | None = None
    ):
        self.user_repo = user_repo
        self.credential_repo = credential_repo
        # Allow injection for testing
        self.password_hasher = password_hasher or PasswordHasher()

    def register_with_password(self, request: RegisterWithPasswordRequest) -> UserProfile:
        """Register a new user with password authentication."""
        if self.user_repo.get_user_by_email(request.email):
            raise UserAlreadyExistsError(field="email")

        if self.user_repo.get_user_by_username(request.username):
            raise UserAlreadyExistsError(field="username")

        # Create user profile
        user = UserProfile(
            user_id=str(uuid.uuid4()),
            username=request.username,
            email=request.email,
            status=UserStatus.INACTIVE,
            roles=["USER"]
        )
        created_user = self.user_repo.create_user(user)

        # Create password credential
        hashed_password = self.password_hasher.hash(request.password)
        credential = UserProfileCredential(
            user_id=created_user.user_id,
            credential_type=CredentialType.PASSWORD,
            credential_identifier=hashed_password,
            is_verified=True
        )
        self.credential_repo.create_credential(credential)

        logger.info(f"Registered user with password: {created_user.user_id}")
        return created_user

    def login_with_password(self, request: LoginWithPasswordRequest) -> UserProfile:
        """Authenticate user with email and password."""
        user = self.user_repo.get_user_by_email(request.email)
        if not user:
            # Generic message to avoid revealing which emails exist
            raise AuthenticationError("Invalid email or password")

        password_cred = self.credential_repo.get_credential_by_type(
            user.user_id,
            CredentialType.PASSWORD
        )
        if not password_cred:
            raise AuthenticationError("Password login not enabled for this account")

        if not self.password_hasher.verify(request.password, password_cred.credential_identifier):
            raise AuthenticationError("Invalid email or password")

        # Update last_used_at
        password_cred.last_used_at = datetime.now(timezone.utc).isoformat()
        self.credential_repo.update_credential(password_cred)

        logger.info(f"User {user.user_id} logged in successfully")
        return user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user's password."""
        user = self.user_repo.get_user(user_id)
        if not user:
            raise UserNotFoundError(user_id=user_id)

        password_cred = self.credential_repo.get_credential_by_type(
            user_id,
            CredentialType.PASSWORD
        )
        if not password_cred:
            raise AuthenticationError("Password credential not found")

        if not self.password_hasher.verify(old_password, password_cred.credential_identifier):
            raise AuthenticationError("Invalid current password")

        password_cred.credential_identifier = self.password_hasher.hash(new_password)
        self.credential_repo.update_credential(password_cred)

        logger.info(f"Password changed for user {user_id}")
        return True
