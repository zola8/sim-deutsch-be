import pytest

from app.iam import UserStatus


class TestCreateUser:
    def test_create_user_success(self, user_repo, sample_user):
        created = user_repo.create_user(sample_user)
        assert created == sample_user
        assert user_repo.get_user(sample_user.user_id) == sample_user

    def test_create_user_duplicate_raises_error(self, user_repo, sample_user):
        user_repo.create_user(sample_user)
        with pytest.raises(ValueError, match="already exists"):
            user_repo.create_user(sample_user)


class TestGetUser:
    def test_get_user_found(self, user_repo, sample_user):
        user_repo.create_user(sample_user)
        result = user_repo.get_user(sample_user.user_id)
        assert result == sample_user

    def test_get_user_not_found_returns_none(self, user_repo):
        result = user_repo.get_user("nonexistent-id")
        assert result is None


class TestGetUserByEmail:
    def test_get_user_by_email_found(self, user_repo, sample_user):
        user_repo.create_user(sample_user)
        result = user_repo.get_user_by_email(sample_user.email)
        assert result == sample_user

    def test_get_user_by_email_not_found_returns_none(self, user_repo):
        result = user_repo.get_user_by_email("not-exist@example.com")
        assert result is None


class TestGetUserByUsername:
    def test_get_user_by_username_found(self, user_repo, sample_user):
        user_repo.create_user(sample_user)
        result = user_repo.get_user_by_username(sample_user.username)
        assert result == sample_user

    def test_get_user_by_username_not_found_returns_none(self, user_repo):
        result = user_repo.get_user_by_username("not-exist")
        assert result is None


class TestGetAllUsers:
    def test_get_all_users_empty(self, user_repo):
        result = user_repo.get_all_users()
        assert result == []

    def test_get_all_users_multiple(self, user_repo, sample_user, another_user):
        user_repo.create_user(sample_user)
        user_repo.create_user(another_user)
        result = user_repo.get_all_users()
        assert len(result) == 2
        assert sample_user in result
        assert another_user in result


class TestUpdateUser:
    def test_update_user_success(self, user_repo, sample_user):
        user_repo.create_user(sample_user)

        updated_user = sample_user.model_copy(update={
            "username": "updated-user",
            "status": UserStatus.ACTIVE
        })
        result = user_repo.update_user(updated_user)

        assert result.username == "updated-user"
        assert result.status == UserStatus.ACTIVE
        assert user_repo.get_user(sample_user.user_id).username == "updated-user"

    def test_update_user_not_found_raises_error(self, user_repo, sample_user):
        with pytest.raises(ValueError, match="not found"):
            user_repo.update_user(sample_user)


class TestDeleteUser:
    def test_delete_user_success(self, user_repo, sample_user):
        user_repo.create_user(sample_user)
        result = user_repo.delete_user(sample_user.user_id)
        assert result is True
        assert user_repo.get_user(sample_user.user_id) is None

    def test_delete_user_not_found_returns_false(self, user_repo):
        result = user_repo.delete_user("not-exist-id")
        assert result is False
