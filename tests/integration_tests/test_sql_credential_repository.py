from datetime import datetime, timezone

import pytest

from app.iam.api.schema_enums import CredentialType
from app.iam.api.schema_user_profile_credential import UserProfileCredential


class TestCreateCredential:
    def test_create_credential_auto_assigns_id(self, credential_repo, db_session, sample_credential):
        assert sample_credential.id is None
        created = credential_repo.create_credential(sample_credential)
        db_session.commit()

        assert created.id is not None
        assert isinstance(created.id, int)

    def test_create_multiple_credentials(self, credential_repo, db_session, sample_credential):
        cred1 = credential_repo.create_credential(sample_credential)

        cred2 = UserProfileCredential(
            user_id="user-123",
            credential_type=CredentialType.OPENID_GOOGLE,
            credential_identifier="google-id",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        cred2 = credential_repo.create_credential(cred2)
        db_session.commit()

        assert cred1.id != cred2.id


class TestGetCredential:
    def test_get_credential_found(self, credential_repo, db_session, sample_credential):
        created = credential_repo.create_credential(sample_credential)
        db_session.commit()

        result = credential_repo.get_credential_by_id(created.id)
        assert result.id == created.id
        assert result.credential_type == CredentialType.PASSWORD

    def test_get_credential_not_found(self, credential_repo):
        assert credential_repo.get_credential_by_id(999) is None


class TestGetCredentialsByUserId:
    def test_get_credentials_by_user_id(self, credential_repo, db_session, sample_credential):
        credential_repo.create_credential(sample_credential)
        db_session.commit()

        result = credential_repo.get_credentials_by_user_id("user-123")
        assert len(result) == 1
        assert result[0].user_id == "user-123"


class TestGetCredentialByType:
    def test_get_credential_by_type_found(self, credential_repo, db_session, sample_credential):
        credential_repo.create_credential(sample_credential)
        db_session.commit()

        result = credential_repo.get_credential_by_type("user-123", CredentialType.PASSWORD)
        assert result is not None
        assert result.credential_type == CredentialType.PASSWORD

    def test_get_credential_by_type_not_found(self, credential_repo, db_session, sample_credential):
        credential_repo.create_credential(sample_credential)
        db_session.commit()

        result = credential_repo.get_credential_by_type("user-123", CredentialType.OPENID_GOOGLE)
        assert result is None


class TestUpdateCredential:
    def test_update_credential_success(self, credential_repo, db_session, sample_credential):
        created = credential_repo.create_credential(sample_credential)
        db_session.commit()

        updated = created.model_copy(update={"is_verified": False})
        credential_repo.update_credential(updated)
        db_session.commit()

        result = credential_repo.get_credential_by_id(created.id)
        assert result.is_verified is False

    def test_update_credential_not_found_raises(self, credential_repo, sample_credential):
        sample_credential.id = 999
        with pytest.raises(ValueError, match="not found"):
            credential_repo.update_credential(sample_credential)


class TestDeleteCredential:
    def test_delete_credential_success(self, credential_repo, db_session, sample_credential):
        created = credential_repo.create_credential(sample_credential)
        db_session.commit()

        assert credential_repo.delete_credential(created.id) is True
        db_session.commit()
        assert credential_repo.get_credential_by_id(created.id) is None

    def test_delete_credential_not_found(self, credential_repo, db_session):
        assert credential_repo.delete_credential(999) is False


class TestDeleteCredentialsByUserId:
    def test_delete_credentials_by_user_id(self, credential_repo, db_session, sample_credential):
        credential_repo.create_credential(sample_credential)
        db_session.commit()

        count = credential_repo.delete_credentials_by_user_id("user-123")
        db_session.commit()

        assert count == 1
        assert credential_repo.get_credentials_by_user_id("user-123") == []
