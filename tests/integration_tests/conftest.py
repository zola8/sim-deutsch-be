from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.iam import (
    SQLAlchemyUserRepository,
    UserProfile,
    UserStatus,
    SQLAlchemyCredentialRepository,
    UserProfileCredential,
    CredentialType
)


@pytest.fixture
def db_session():
    """
    Creates an in-memory SQLite database for testing.
    Yields a session, then tears everything down.
    """
    # Use in-memory SQLite (fast, isolated, no file)
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def user_repo(db_session):
    return SQLAlchemyUserRepository(db=db_session)


@pytest.fixture
def credential_repo(db_session):
    return SQLAlchemyCredentialRepository(db=db_session)


@pytest.fixture
def sample_user():
    return UserProfile(
        user_id="user-123",
        username="testuser",
        email="test@example.com",
        status=UserStatus.INACTIVE,
        created_at=datetime.now(timezone.utc).isoformat(),
        roles=["USER"]
    )


@pytest.fixture
def sample_credential():
    return UserProfileCredential(
        user_id="user-123",
        credential_type=CredentialType.PASSWORD,
        credential_identifier="hashed_pw",
        is_verified=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )
