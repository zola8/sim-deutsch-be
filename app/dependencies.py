from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import PasswordHasher
from app.iam.orm.base import UserRepository, CredentialRepository
from app.iam.orm.sql_credential_repo import SQLAlchemyCredentialRepository
from app.iam.orm.sql_user_profile_repo import SQLAlchemyUserRepository
from app.iam.services.authentication_service import AuthService
from app.iam.services.email_service import EmailService
from app.iam.services.jwt_token_service import TokenService
from app.iam.services.user_profile_service import UserService


# --- Repository Dependencies ---

def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return SQLAlchemyUserRepository(db=db)


def get_credential_repo(db: Session = Depends(get_db)) -> CredentialRepository:
    return SQLAlchemyCredentialRepository(db=db)


# --- Utility Dependencies ---

def get_password_hasher() -> PasswordHasher:
    # Stateless, so we can create a new instance each time (cheap)
    return PasswordHasher()


# --- Service Dependencies ---

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserService:
    return UserService(user_repo=user_repo)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    credential_repo: CredentialRepository = Depends(get_credential_repo),
    password_hasher: PasswordHasher = Depends(get_password_hasher)
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        credential_repo=credential_repo,
        password_hasher=password_hasher,
        token_service=TokenService(settings.JWT_SECRET_KEY, expire_minutes=settings.auth_config.token_expire_minutes),
        email_service=EmailService(),
        auth_config=settings.auth_config
    )


# --- Type Aliases ---

UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
CredentialRepoDep = Annotated[CredentialRepository, Depends(get_credential_repo)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
