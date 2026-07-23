import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.iam.orm.base import CredentialRepository
from app.iam.orm.models import CredentialModel
from app.iam.api.schema_enums import CredentialType
from app.iam.api.schema_user_profile_credential import UserProfileCredential

logger = logging.getLogger(__name__)


class SQLAlchemyCredentialRepository(CredentialRepository):
    """SQLAlchemy implementation of CredentialRepository."""

    def __init__(self, db: Session):
        self.db = db

    def create_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        model = self._to_model(credential)
        self.db.add(model)
        self.db.flush()  # Populates the auto-increment ID

        # Update the Pydantic object with the DB-generated ID
        credential.id = model.id
        logger.debug(f"Created credential {model.id} for user {credential.user_id}")
        return credential

    def get_credential(self, credential_id: int) -> Optional[UserProfileCredential]:
        model = self.db.execute(
            select(CredentialModel).where(credential_id == CredentialModel.id)
        ).scalar_one_or_none()
        return self._to_schema(model) if model else None

    def get_credentials_by_user_id(self, user_id: str) -> List[UserProfileCredential]:
        models = self.db.execute(
            select(CredentialModel).where(user_id == CredentialModel.user_id)
        ).scalars().all()
        return [self._to_schema(m) for m in models]

    def get_credential_by_type(
        self,
        user_id: str,
        credential_type: CredentialType
    ) -> Optional[UserProfileCredential]:
        model = self.db.execute(
            select(CredentialModel).where(
                user_id == CredentialModel.user_id,
                credential_type == CredentialModel.credential_type
            )
        ).scalar_one_or_none()
        return self._to_schema(model) if model else None

    def update_credential(self, credential: UserProfileCredential) -> UserProfileCredential:
        model = self.db.execute(
            select(CredentialModel).where(credential.id == CredentialModel.id)
        ).scalar_one_or_none()

        if not model:
            raise ValueError(f"Credential with id {credential.id} not found")

        # Update fields
        model.credential_identifier = credential.credential_identifier
        model.credential_secret = credential.credential_secret
        model.is_verified = credential.is_verified
        model.last_used_at = (
            datetime.fromisoformat(credential.last_used_at)
            if credential.last_used_at else None
        )

        self.db.flush()
        logger.debug(f"Updated credential: {credential.id}")
        return credential

    def delete_credential(self, credential_id: int) -> bool:
        model = self.db.execute(
            select(CredentialModel).where(credential_id == CredentialModel.id)
        ).scalar_one_or_none()

        if not model:
            return False

        self.db.delete(model)
        self.db.flush()
        logger.debug(f"Deleted credential: {credential_id}")
        return True

    def delete_credentials_by_user_id(self, user_id: str) -> int:
        models = self.db.execute(
            select(CredentialModel).where(user_id == CredentialModel.user_id)
        ).scalars().all()

        count = len(models)
        for model in models:
            self.db.delete(model)

        if count > 0:
            self.db.flush()
            logger.debug(f"Deleted {count} credentials for user {user_id}")

        return count

    # --- Conversion helpers ---

    def _to_model(self, credential: UserProfileCredential) -> CredentialModel:
        return CredentialModel(
            # Don't set id - let DB auto-increment handle it
            user_id=credential.user_id,
            credential_type=credential.credential_type,
            credential_identifier=credential.credential_identifier,
            credential_secret=credential.credential_secret,
            is_verified=credential.is_verified,
            created_at=(
                datetime.fromisoformat(credential.created_at)
                if credential.created_at else None
            ),
            last_used_at=(
                datetime.fromisoformat(credential.last_used_at)
                if credential.last_used_at else None
            )
        )

    def _to_schema(self, model: CredentialModel) -> UserProfileCredential:
        return UserProfileCredential(
            id=model.id,
            user_id=model.user_id,
            credential_type=model.credential_type,
            credential_identifier=model.credential_identifier,
            credential_secret=model.credential_secret,
            is_verified=model.is_verified,
            created_at=model.created_at.isoformat() if model.created_at else None,
            last_used_at=model.last_used_at.isoformat() if model.last_used_at else None
        )
