from datetime import datetime, timezone

from app.iam.api.schema_enums import CredentialType
from app.iam.api.schema_user_profile import UserProfile
from app.iam.api.schema_user_profile_credential import UserProfileCredential


def test_deleting_user_cascades_to_credentials(
    user_repo, credential_repo, db_session
):
    """
    CRITICAL TEST: When a user is deleted, their credentials must be
    automatically deleted by the database cascade.

    This is DIFFERENT from the in-memory repository behavior.
    """
    # Create user
    user = UserProfile(
        user_id="user-123",
        username="testuser",
        email="test@example.com",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    user_repo.create_user(user)

    # Create 2 credentials for the user
    cred1 = UserProfileCredential(
        user_id=user.user_id,
        credential_type=CredentialType.PASSWORD,
        credential_identifier="hash1",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    cred2 = UserProfileCredential(
        user_id=user.user_id,
        credential_type=CredentialType.OPENID_GOOGLE,
        credential_identifier="google-id",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    credential_repo.create_credential(cred1)
    credential_repo.create_credential(cred2)
    db_session.commit()

    # Verify setup
    assert len(credential_repo.get_credentials_by_user_id(user.user_id)) == 2

    # Delete the user
    user_repo.delete_user(user.user_id)
    db_session.commit()

    # CRITICAL: Credentials must be gone too (cascade)
    remaining_creds = credential_repo.get_credentials_by_user_id(user.user_id)
    assert len(remaining_creds) == 0, "Cascade failed: orphaned credentials remain!"
