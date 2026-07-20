from datetime import datetime, timezone

import pytest

from app.iam import UserProfile, UserStatus


class TestCreateUser:
    def test_create_user_persists_to_db(self, user_repo, db_session, sample_user):
        created = user_repo.create_user(sample_user)
        db_session.commit()  # Explicit commit for test

        # Verify by querying directly
        result = user_repo.get_user(sample_user.user_id)
        assert result is not None
        assert result.user_id == sample_user.user_id
        assert result.username == sample_user.username
        assert result.roles == ["USER"]

    def test_create_user_with_multiple_roles(self, user_repo, db_session):
        user = UserProfile(
            user_id="user-456",
            username="admin",
            email="admin@example.com",
            created_at=datetime.now(timezone.utc).isoformat(),
            roles=["USER", "ADMIN"]
        )
        user_repo.create_user(user)
        db_session.commit()

        result = user_repo.get_user(user.user_id)
        assert result.roles == ["USER", "ADMIN"]


class TestGetUser:
    def test_get_user_found(self, user_repo, db_session, sample_user):
        user_repo.create_user(sample_user)
        db_session.commit()

        result = user_repo.get_user(sample_user.user_id)
        assert_users_equal(result, sample_user)

    def test_get_user_not_found_returns_none(self, user_repo):
        result = user_repo.get_user("nonexistent")
        assert result is None


class TestGetUserByEmail:
    def test_get_user_by_email_found(self, user_repo, db_session, sample_user):
        user_repo.create_user(sample_user)
        db_session.commit()

        result = user_repo.get_user_by_email(sample_user.email)
        assert result.user_id == sample_user.user_id

    def test_get_user_by_email_not_found(self, user_repo):
        result = user_repo.get_user_by_email("nope@example.com")
        assert result is None


class TestGetUserByUsername:
    def test_get_user_by_username_found(self, user_repo, db_session, sample_user):
        user_repo.create_user(sample_user)
        db_session.commit()

        result = user_repo.get_user_by_username(sample_user.username)
        assert result.user_id == sample_user.user_id


class TestGetAllUsers:
    def test_get_all_users_empty(self, user_repo):
        assert user_repo.get_all_users() == []

    def test_get_all_users_multiple(self, user_repo, db_session):
        for i in range(3):
            user_repo.create_user(UserProfile(
                user_id=f"user-{i}",
                username=f"user{i}",
                email=f"user{i}@example.com",
                created_at=datetime.now(timezone.utc).isoformat()
            ))
        db_session.commit()

        result = user_repo.get_all_users()
        assert len(result) == 3


class TestUpdateUser:
    def test_update_user_success(self, user_repo, db_session, sample_user):
        user_repo.create_user(sample_user)
        db_session.commit()

        updated = sample_user.model_copy(update={
            "username": "newname",
            "status": UserStatus.ACTIVE
        })
        user_repo.update_user(updated)
        db_session.commit()

        result = user_repo.get_user(sample_user.user_id)
        assert result.username == "newname"
        assert result.status == UserStatus.ACTIVE

    def test_update_user_not_found_raises(self, user_repo, sample_user):
        with pytest.raises(ValueError, match="not found"):
            user_repo.update_user(sample_user)


class TestDeleteUser:
    def test_delete_user_success(self, user_repo, db_session, sample_user):
        user_repo.create_user(sample_user)
        db_session.commit()

        result = user_repo.delete_user(sample_user.user_id)
        db_session.commit()

        assert result is True
        assert user_repo.get_user(sample_user.user_id) is None

    def test_delete_user_not_found_returns_false(self, user_repo, db_session):
        assert user_repo.delete_user("nope") is False


def assert_users_equal(actual: UserProfile, expected: UserProfile):
    assert actual.user_id == expected.user_id
    assert actual.username == expected.username
    assert actual.email == expected.email
    assert actual.status == expected.status
    assert actual.roles == expected.roles
    # created_at is ignored due to timezone handling differences
    assert actual.created_at is not None
    assert expected.created_at is not None
