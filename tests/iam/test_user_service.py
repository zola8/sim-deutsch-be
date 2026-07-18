from datetime import datetime

import pytest
from pydantic import ValidationError

from app.iam.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.iam.repositories import InMemoryUserRepository
from app.iam.schemas import (
    UserCreateRequest,
    UserCreateResponse,
    UserUpdateRequest,
    UserStatus, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH
)
from app.iam.user_service import UserService

# --- TEST CONSTANTS ---
FAKE_ID = "12345678-1234-5678-1234-567812345678"
TEST_USERNAME = "testuser"
TEST_EMAIL = "test@example.com"


# --- FIXTURES ---

@pytest.fixture
def user_service():
    """Provides a fresh UserService with an empty InMemoryUserRepository for each test."""
    repo = InMemoryUserRepository()
    return UserService(user_repo=repo)


@pytest.fixture
def valid_create_request():
    """Provides a standard, valid UserCreateRequest."""
    return UserCreateRequest(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password="securepassword",
        password_repeat="securepassword"
    )


# --- CREATE USER + GET USER ---

def test_create_user_success(user_service, valid_create_request):
    response = user_service.create_user(valid_create_request)

    # 1. Check the response object
    assert isinstance(response, UserCreateResponse)
    assert response.status == UserStatus.INACTIVE
    assert len(response.user_id) == 36

    # 2. Verify it was actually saved in the repository
    profile = user_service.get_user(response.user_id)
    assert profile.username == TEST_USERNAME
    assert profile.email == TEST_EMAIL
    assert profile.password == "securepassword"
    assert profile.status == UserStatus.INACTIVE
    assert profile.created_at is not None
    assert isinstance(datetime.fromisoformat(profile.created_at), datetime)
    assert 'USER' in profile.roles


def test_create_user_duplicate_email(user_service, valid_create_request):
    user_service.create_user(valid_create_request)

    duplicate_request = UserCreateRequest(
        username="anotheruser",
        email=valid_create_request.email,
        password="password123",
        password_repeat="password123"
    )

    with pytest.raises(UserAlreadyExistsError) as exc_info:
        user_service.create_user(duplicate_request)

    assert exc_info.value.field == "email"


def test_create_user_short_password(user_service, valid_create_request):
    pwd = "*" * (MIN_PASSWORD_LENGTH - 1)

    with pytest.raises(ValidationError):
        UserCreateRequest(
            username=valid_create_request.username,
            email=valid_create_request.email,
            password=pwd,
            password_repeat=pwd
        )


def test_create_user_long_password(user_service, valid_create_request):
    pwd = "*" * (MAX_PASSWORD_LENGTH + 1)

    with pytest.raises(ValidationError):
        UserCreateRequest(
            username=valid_create_request.username,
            email=valid_create_request.email,
            password=pwd,
            password_repeat=pwd
        )


def test_create_user_short_username(user_service, valid_create_request):
    username = "a" * (MIN_USERNAME_LENGTH - 1)

    with pytest.raises(ValidationError):
        UserCreateRequest(
            username=username,
            email=valid_create_request.email,
            password=valid_create_request.password,
            password_repeat=valid_create_request.password
        )


def test_create_user_long_username(user_service, valid_create_request):
    username = "a" * (MAX_USERNAME_LENGTH + 1)

    with pytest.raises(ValidationError):
        UserCreateRequest(
            username=username,
            email=valid_create_request.email,
            password=valid_create_request.password,
            password_repeat=valid_create_request.password
        )


# --- GET USER ---

def test_get_user_not_found(user_service):
    with pytest.raises(UserNotFoundError):
        user_service.get_user(FAKE_ID)


# --- GET ALL USERS TESTS ---

def test_get_all_users_empty(user_service):
    users = user_service.get_all_users()
    assert users == []


def test_get_all_users_multiple(user_service, valid_create_request):
    user_service.create_user(valid_create_request)

    second_request = UserCreateRequest(
        username=valid_create_request.username + "2",
        email="user2@example.com",
        password=valid_create_request.password,
        password_repeat=valid_create_request.password
    )
    user_service.create_user(second_request)

    users = user_service.get_all_users()
    assert len(users) == 2


# --- UPDATE USER TESTS ---

def test_update_user_success(user_service, valid_create_request):
    created = user_service.create_user(valid_create_request)
    user_id = created.user_id

    update_req = UserUpdateRequest(username="updated_name", status=UserStatus.ACTIVE)
    updated_profile = user_service.update_user(user_id, update_req)

    assert updated_profile.username == "updated_name"
    assert updated_profile.status == UserStatus.ACTIVE
    assert updated_profile.email == TEST_EMAIL


def test_update_user_not_found(user_service):
    update_req = UserUpdateRequest(username="other_name", status=UserStatus.ACTIVE)

    with pytest.raises(UserNotFoundError):
        user_service.update_user(FAKE_ID, update_req)


# --- DELETE USER TESTS ---

def test_delete_user_success_soft_delete(user_service, valid_create_request):
    created = user_service.create_user(valid_create_request)
    user_id = created.user_id

    response = user_service.delete_user(user_id)

    # Check the response
    assert isinstance(response, UserCreateResponse)
    assert response.status == UserStatus.DELETED

    # Verify it's a soft delete
    profile = user_service.get_user(user_id)
    assert profile.status == UserStatus.DELETED
    assert profile.username == TEST_USERNAME


def test_delete_user_not_found(user_service):
    with pytest.raises(UserNotFoundError):
        user_service.delete_user(FAKE_ID)
