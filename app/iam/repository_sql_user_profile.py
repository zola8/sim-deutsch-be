import json
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.iam.models import UserModel
from app.iam.repository_base import UserRepository
from app.iam.schema_user_profile import UserProfile

logger = logging.getLogger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserProfile) -> UserProfile:
        model = self._to_model(user)
        self.db.add(model)
        self.db.flush()  # Ensures any DB-generated values are populated
        logger.debug(f"Created user: {user.user_id}")
        return self._to_schema(model)

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        model = self.db.execute(
            select(UserModel).where(user_id == UserModel.user_id)
        ).scalar_one_or_none()
        return self._to_schema(model) if model else None

    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        model = self.db.execute(
            select(UserModel).where(email == UserModel.email)
        ).scalar_one_or_none()
        return self._to_schema(model) if model else None

    def get_user_by_username(self, username: str) -> Optional[UserProfile]:
        model = self.db.execute(
            select(UserModel).where(username == UserModel.username)
        ).scalar_one_or_none()
        return self._to_schema(model) if model else None

    def get_all_users(self) -> List[UserProfile]:
        models = self.db.execute(select(UserModel)).scalars().all()
        return [self._to_schema(m) for m in models]

    def update_user(self, user: UserProfile) -> UserProfile:
        model = self.db.execute(
            select(UserModel).where(user.user_id == UserModel.user_id)
        ).scalar_one_or_none()

        if not model:
            raise ValueError(f"User with id {user.user_id} not found")

        # Update fields
        model.username = user.username
        model.email = user.email
        model.status = user.status
        model.roles = json.dumps(user.roles)

        self.db.flush()
        logger.debug(f"Updated user: {user.user_id}")
        return self._to_schema(model)

    def delete_user(self, user_id: str) -> bool:
        model = self.db.execute(
            select(UserModel).where(user_id == UserModel.user_id)
        ).scalar_one_or_none()

        if not model:
            return False

        # SQLAlchemy cascade will handle credential deletion automatically
        self.db.delete(model)
        self.db.flush()
        logger.debug(f"Deleted user: {user_id}")
        return True

    # --- Conversion helpers ---

    def _to_model(self, user: UserProfile) -> UserModel:
        return UserModel(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            status=user.status,
            created_at=datetime.fromisoformat(user.created_at) if user.created_at else None,
            roles=json.dumps(user.roles) if user.roles else "[]"
        )

    def _to_schema(self, model: UserModel) -> UserProfile:
        return UserProfile(
            user_id=model.user_id,
            username=model.username,
            email=model.email,
            status=model.status,
            created_at=model.created_at.isoformat() if model.created_at else None,
            roles=json.loads(model.roles) if model.roles else []
        )
