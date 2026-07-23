from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, EmailStr

from app.core.exception_handlers import register_exception_handlers
from app.core.security import PasswordHasher
from app.iam.api.schema_enums import CredentialType, UserStatus
from app.iam.api.schema_user_profile import UserProfile
from app.iam.api.schema_user_profile_credential import UserProfileCredential
from app.iam.exceptions import UserNotFoundError, UserAlreadyExistsError
from app.iam.orm.repository_in_memory import InMemoryCredentialRepository, InMemoryUserRepository


@pytest.fixture
def test_app():
    """Create a minimal FastAPI app with exception handlers and dummy routes."""
    app = FastAPI()
    register_exception_handlers(app)

    # Dummy routes that raise our exceptions
    @app.get("/trigger/not-found")
    def trigger_not_found():
        raise UserNotFoundError(user_id="missing-id")

    @app.get("/trigger/already-exists")
    def trigger_already_exists():
        raise UserAlreadyExistsError(field="email")

    @app.get("/trigger/not-found-no-id")
    def trigger_not_found_no_id():
        raise UserNotFoundError()

    @app.get("/trigger/unhandled")
    def trigger_unhandled():
        raise RuntimeError("Something went terribly wrong")

    # Route with Pydantic validation to trigger RequestValidationError
    class DummyPayload(BaseModel):
        email: EmailStr
        age: int

    @app.post("/trigger/validation")
    def trigger_validation(payload: DummyPayload):
        return payload

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def credential_repo():
    """Fresh repository instance for each test."""
    return InMemoryCredentialRepository()


@pytest.fixture
def sample_credential():
    """Sample credential for testing."""
    return UserProfileCredential(
        user_id="user-123",
        credential_type=CredentialType.PASSWORD,
        credential_identifier="hashed_password_123",
        credential_secret="salt_abc",
        is_verified=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )


@pytest.fixture
def oauth_credential():
    """Sample OAuth credential for testing."""
    return UserProfileCredential(
        user_id="user-123",
        credential_type=CredentialType.OPENID_GOOGLE,
        credential_identifier="google-oauth-id-456",
        is_verified=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )


@pytest.fixture
def another_user_credential():
    """Credential for a different user."""
    return UserProfileCredential(
        user_id="user-456",
        credential_type=CredentialType.PASSWORD,
        credential_identifier="hashed_password_789",
        is_verified=False,
        created_at=datetime.now(timezone.utc).isoformat()
    )


@pytest.fixture
def user_repo():
    """Fresh repository instance for each test."""
    return InMemoryUserRepository()


@pytest.fixture
def sample_user():
    """Sample user profile for testing."""
    return UserProfile(
        user_id="user-123",
        username="testuser",
        email="test@example.com",
        status=UserStatus.INACTIVE,
        created_at=datetime.now(timezone.utc).isoformat(),
        roles=["USER"]
    )


@pytest.fixture
def another_user():
    """Another sample user for multi-user tests."""
    return UserProfile(
        user_id="user-456",
        username="anotheruser",
        email="another@example.com",
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc).isoformat(),
        roles=["USER", "ADMIN"]
    )


@pytest.fixture
def hasher():
    return PasswordHasher()
