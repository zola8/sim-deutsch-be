import logging
import uuid
from datetime import datetime, timezone

from app.core.config import AuthConfig
from app.core.security import PasswordHasher
from app.iam.api.schema_authentication import RegisterWithPasswordRequest, LoginWithPasswordRequest
from app.iam.api.schema_enums import UserStatus, CredentialType
from app.iam.api.schema_user_profile import UserProfile
from app.iam.api.schema_user_profile_credential import UserProfileCredential
from app.iam.exceptions import UserAlreadyExistsError, AuthenticationError, UserNotFoundError
from app.iam.orm.base import UserRepository, CredentialRepository
from app.iam.services.email_service import EmailService
from app.iam.services.jwt_token_service import TokenService

logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling authentication (password, OAuth)."""

    def __init__(
        self,
        user_repo: UserRepository,
        credential_repo: CredentialRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        email_service: EmailService,
        auth_config: AuthConfig
    ):
        self.user_repo = user_repo
        self.credential_repo = credential_repo
        self.password_hasher = password_hasher
        self.token_service = token_service
        self.email_service = email_service
        self.auth_config = auth_config

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
            created_at=datetime.now().isoformat(),
            roles=["USER"]
        )
        created_user = self.user_repo.create_user(user)

        # Create password credential
        hashed_password = self.password_hasher.hash(request.password)
        credential = UserProfileCredential(
            user_id=created_user.user_id,
            credential_type=CredentialType.PASSWORD,
            credential_identifier=hashed_password,
            is_verified=False
        )
        created_credential = self.credential_repo.create_credential(credential)

        # Generate token and send email
        token = self.token_service.generate_activation_token(
            user_id=created_user.user_id,
            credential_id=created_credential.id
        )

        activation_link = f"{self.auth_config.frontend_base_url}/activate?token={token}"
        self.email_service.send_activation_email(created_user.email, created_user.username, activation_link)

        logger.info(f"Registered user with password: {created_user.user_id}. Activation email sent.")
        return created_user


    def activate_user(self, token: str) -> UserProfile:
        # 1. Extract IDs from the token
        user_id, credential_id = self.token_service.verify_activation_token(token)

        # 2. Update user status
        updated_user = self.user_repo.update_user_status(user_id, UserStatus.ACTIVE)

        # 3. Fetch the existing credential to get its current state
        credential = self.credential_repo.get_credential_by_id(credential_id)
        if not credential:
            raise ValueError(f"Credential {credential_id} not found")

        # 4. Mutate the domain object
        credential.is_verified = True

        # 5. Persist using your existing generic update method
        self.credential_repo.update_credential(credential)

        logger.info(f"User activated and credential verified: {user_id}")
        return updated_user


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
        user = self.user_repo.get_user_by_id(user_id)
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
