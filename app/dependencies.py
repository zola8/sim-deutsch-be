from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import PasswordHasher
from app.iam.orm.repository_base import UserRepository, CredentialRepository
from app.iam.orm.repository_sql_credential import SQLAlchemyCredentialRepository
from app.iam.orm.repository_sql_user_profile import SQLAlchemyUserRepository
from app.iam.service_auth import AuthService
from app.iam.service_user import UserService


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
        password_hasher=password_hasher
    )


# --- Type Aliases ---

UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
CredentialRepoDep = Annotated[CredentialRepository, Depends(get_credential_repo)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
