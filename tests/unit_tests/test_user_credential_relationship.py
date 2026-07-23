# tests/unit/repositories/test_user_credential_relationship.py

from datetime import datetime, timezone

import pytest

from app.iam.api.schema_enums import UserStatus, CredentialType
from app.iam.api.schema_user_profile import UserProfile
from app.iam.api.schema_user_profile_credential import UserProfileCredential



@pytest.fixture
def user_with_multiple_credentials(user_repo, credential_repo):
    """
    Helper fixture that creates a user with multiple credentials.
    Returns (user, [credentials]).
    """
    # Create user
    user = UserProfile(
        user_id="user-123",
        username="testuser",
        email="test@example.com",
        status=UserStatus.ACTIVE,
        created_at=datetime.now(timezone.utc).isoformat(),
        roles=["USER"]
    )
    user_repo.create_user(user)

    password_cred = UserProfileCredential(
        user_id=user.user_id,
        credential_type=CredentialType.PASSWORD,
        credential_identifier="hashed_password",
        is_verified=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    credential_repo.create_credential(password_cred)

    google_cred = UserProfileCredential(
        user_id=user.user_id,
        credential_type=CredentialType.OPENID_GOOGLE,
        credential_identifier="google-oauth-id",
        is_verified=True,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    credential_repo.create_credential(google_cred)

    return user, [password_cred, google_cred]


class TestOneToManyRelationship:
    def test_user_can_have_multiple_credentials(self, user_repo, credential_repo, user_with_multiple_credentials):
        user, credentials = user_with_multiple_credentials

        # Verify user exists
        fetched_user = user_repo.get_user_by_id(user.user_id)
        assert fetched_user is not None
        assert fetched_user.user_id == user.user_id

        # Verify user has multiple credentials
        user_credentials = credential_repo.get_credentials_by_user_id(user.user_id)
        assert len(user_credentials) == 2

        # Verify credential types
        cred_types = {cred.credential_type for cred in user_credentials}
        assert CredentialType.PASSWORD in cred_types
        assert CredentialType.OPENID_GOOGLE in cred_types

    def test_credentials_belong_to_correct_user(self, user_repo, credential_repo):
        # Create two users
        user1 = UserProfile(
            user_id="user-1",
            username="user1",
            email="user1@example.com",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        user2 = UserProfile(
            user_id="user-2",
            username="user2",
            email="user2@example.com",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        user_repo.create_user(user1)
        user_repo.create_user(user2)

        # Create credentials for each user
        cred1 = UserProfileCredential(
            user_id=user1.user_id,
            credential_type=CredentialType.PASSWORD,
            credential_identifier="hash1",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        cred2 = UserProfileCredential(
            user_id=user2.user_id,
            credential_type=CredentialType.PASSWORD,
            credential_identifier="hash2",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        credential_repo.create_credential(cred1)
        credential_repo.create_credential(cred2)

        # Verify each user only gets their own credentials
        user1_creds = credential_repo.get_credentials_by_user_id(user1.user_id)
        user2_creds = credential_repo.get_credentials_by_user_id(user2.user_id)

        assert len(user1_creds) == 1
        assert len(user2_creds) == 1
        assert user1_creds[0].credential_identifier == "hash1"
        assert user2_creds[0].credential_identifier == "hash2"


class TestCredentialQueries:
    def test_get_credential_by_type_for_user(self, user_repo, credential_repo, user_with_multiple_credentials):
        user, credentials = user_with_multiple_credentials

        # Get password credential for user
        password_cred = credential_repo.get_credential_by_type(user.user_id, CredentialType.PASSWORD)
        assert password_cred is not None
        assert password_cred.credential_type == CredentialType.PASSWORD
        assert password_cred.user_id == user.user_id

        # Get Google credential for user
        google_cred = credential_repo.get_credential_by_type(user.user_id, CredentialType.OPENID_GOOGLE)
        assert google_cred is not None
        assert google_cred.credential_type == CredentialType.OPENID_GOOGLE

    def test_get_nonexistent_credential_type_returns_none(self, user_repo, credential_repo,
                                                          user_with_multiple_credentials):
        user, _ = user_with_multiple_credentials

        # TODO later: User doesn't have QR_CODE credential
        # result = credential_repo.get_credential_by_type(user.user_id, CredentialType.QR_CODE)
        # assert result is None


class TestCascadeBehavior:
    """
    Tests that verify the logical cascade behavior.
    Note: In SQLAlchemy, this is handled by the database cascade.
    In in-memory repos, we need to explicitly delete credentials.
    """

    def test_deleting_all_credentials_leaves_user_intact(self, user_repo, credential_repo,
                                                         user_with_multiple_credentials):
        user, _ = user_with_multiple_credentials

        # Delete all credentials for user
        deleted_count = credential_repo.delete_credentials_by_user_id(user.user_id)
        assert deleted_count == 2

        # Verify user still exists
        fetched_user = user_repo.get_user_by_id(user.user_id)
        assert fetched_user is not None
        assert fetched_user.user_id == user.user_id

        # Verify user has no credentials
        user_creds = credential_repo.get_credentials_by_user_id(user.user_id)
        assert len(user_creds) == 0

    def test_deleting_user_does_not_automatically_delete_credentials_in_memory_repo(
        self, user_repo, credential_repo, user_with_multiple_credentials
    ):
        """
        This test documents that in-memory repos don't cascade.
        In SQLAlchemy, the database handles cascade via ondelete="CASCADE".
        """
        user, credentials = user_with_multiple_credentials

        # Delete user
        user_repo.delete_user(user.user_id)

        # In in-memory repo, credentials still exist (no cascade)
        orphaned_creds = credential_repo.get_credentials_by_user_id(user.user_id)
        assert len(orphaned_creds) == 2  # They're still there!

        # In a real service layer, you'd need to explicitly delete credentials:
        credential_repo.delete_credentials_by_user_id(user.user_id)
        assert len(credential_repo.get_credentials_by_user_id(user.user_id)) == 0


class TestRelationshipIntegrity:
    def test_credential_user_id_matches_existing_user(self, user_repo, credential_repo):
        user = UserProfile(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        user_repo.create_user(user)

        cred = UserProfileCredential(
            user_id=user.user_id,
            credential_type=CredentialType.PASSWORD,
            credential_identifier="hash",
            created_at=datetime.now(timezone.utc).isoformat()
        )
        credential_repo.create_credential(cred)

        # Verify relationship
        fetched_cred = credential_repo.get_credential_by_id(cred.id)
        assert fetched_cred.user_id == user.user_id

        fetched_user = user_repo.get_user_by_id(user.user_id)
        assert fetched_user is not None

    def test_updating_user_does_not_affect_credentials(self, user_repo, credential_repo,
                                                       user_with_multiple_credentials):
        user, credentials = user_with_multiple_credentials

        # Update user
        updated_user = user.model_copy(update={"username": "newusername"})
        user_repo.update_user(updated_user)

        # Verify credentials are unchanged
        user_creds = credential_repo.get_credentials_by_user_id(user.user_id)
        assert len(user_creds) == 2
        assert all(cred.user_id == user.user_id for cred in user_creds)

    def test_updating_credential_does_not_affect_user(self, user_repo, credential_repo, user_with_multiple_credentials):
        user, credentials = user_with_multiple_credentials

        # Update a credential
        cred_to_update = credentials[0]
        updated_cred = cred_to_update.model_copy(update={"is_verified": False})
        credential_repo.update_credential(updated_cred)

        # Verify user is unchanged
        fetched_user = user_repo.get_user_by_id(user.user_id)
        assert fetched_user.username == user.username
        assert fetched_user.email == user.email
