from datetime import datetime, timezone

import pytest

from app.iam import UserProfileCredential, CredentialType


class TestCreateCredential:
    def test_create_credential_auto_assigns_id(self, credential_repo, sample_credential):
        assert sample_credential.id is None
        created = credential_repo.create_credential(sample_credential)
        assert created.id is not None
        assert created.id == 1

    def test_create_credential_increments_id(self, credential_repo, sample_credential, oauth_credential):
        cred1 = credential_repo.create_credential(sample_credential)
        cred2 = credential_repo.create_credential(oauth_credential)
        assert cred1.id == 1
        assert cred2.id == 2

    def test_create_credential_preserves_provided_id(self, credential_repo):
        cred = UserProfileCredential(
            id=999,
            user_id="user-123",
            credential_type=CredentialType.PASSWORD,
            credential_identifier="hash",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        created = credential_repo.create_credential(cred)
        assert created.id == 999


class TestGetCredential:
    def test_get_credential_found(self, credential_repo, sample_credential):
        created = credential_repo.create_credential(sample_credential)
        result = credential_repo.get_credential(created.id)
        assert result == created

    def test_get_credential_not_found_returns_none(self, credential_repo):
        result = credential_repo.get_credential(999)
        assert result is None


class TestGetCredentialsByUserId:
    def test_get_credentials_by_user_id_empty(self, credential_repo):
        result = credential_repo.get_credentials_by_user_id("not-exist-user")
        assert result == []

    def test_get_credentials_by_user_id_multiple(self, credential_repo, sample_credential, oauth_credential,
                                                 another_user_credential):
        credential_repo.create_credential(sample_credential)
        credential_repo.create_credential(oauth_credential)
        credential_repo.create_credential(another_user_credential)

        result = credential_repo.get_credentials_by_user_id("user-123")
        assert len(result) == 2
        assert all(cred.user_id == "user-123" for cred in result)


class TestGetCredentialByType:
    def test_get_credential_by_type_found(self, credential_repo, sample_credential, oauth_credential):
        credential_repo.create_credential(sample_credential)
        credential_repo.create_credential(oauth_credential)

        result = credential_repo.get_credential_by_type("user-123", CredentialType.PASSWORD)
        assert result is not None
        assert result.credential_type == CredentialType.PASSWORD

    def test_get_credential_by_type_not_found_returns_none(self, credential_repo, sample_credential):
        credential_repo.create_credential(sample_credential)

        result = credential_repo.get_credential_by_type("user-123", CredentialType.OPENID_GOOGLE)
        assert result is None


class TestUpdateCredential:
    def test_update_credential_success(self, credential_repo, sample_credential):
        created = credential_repo.create_credential(sample_credential)

        updated = created.model_copy(update={
            "is_verified": False,
            "last_used_at": datetime.now(timezone.utc).isoformat()
        })
        result = credential_repo.update_credential(updated)

        assert result.is_verified is False
        assert result.last_used_at is not None
        assert credential_repo.get_credential(created.id).is_verified is False

    def test_update_credential_not_found_raises_error(self, credential_repo, sample_credential):
        sample_credential.id = 999
        with pytest.raises(ValueError, match="not found"):
            credential_repo.update_credential(sample_credential)


class TestDeleteCredential:
    def test_delete_credential_success(self, credential_repo, sample_credential):
        created = credential_repo.create_credential(sample_credential)
        result = credential_repo.delete_credential(created.id)
        assert result is True
        assert credential_repo.get_credential(created.id) is None

    def test_delete_credential_not_found_returns_false(self, credential_repo):
        result = credential_repo.delete_credential(999)
        assert result is False


class TestDeleteCredentialsByUserId:
    def test_delete_credentials_by_user_id_success(self, credential_repo, sample_credential, oauth_credential,
                                                   another_user_credential):
        credential_repo.create_credential(sample_credential)
        credential_repo.create_credential(oauth_credential)
        credential_repo.create_credential(another_user_credential)

        deleted_count = credential_repo.delete_credentials_by_user_id("user-123")
        assert deleted_count == 2
        assert len(credential_repo.get_credentials_by_user_id("user-123")) == 0
        assert len(credential_repo.get_credentials_by_user_id("user-456")) == 1

    def test_delete_credentials_by_user_id_none_returns_zero(self, credential_repo):
        deleted_count = credential_repo.delete_credentials_by_user_id("not-exist-user")
        assert deleted_count == 0
