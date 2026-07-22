from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base
from app.iam.api.schema_enums import UserStatus, CredentialType


class UserModel(Base):
    __tablename__ = "user_profiles"

    user_id = mapped_column(String, primary_key=True, index=True)
    username = mapped_column(String, unique=True, nullable=False, index=True)
    email = mapped_column(String, unique=True, nullable=False, index=True)
    status = mapped_column(SQLEnum(UserStatus), default=UserStatus.INACTIVE, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    roles = mapped_column(String, default="[]")  # Store as JSON string

    # Relationship: one user has many credentials
    credentials = relationship(
        "CredentialModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class CredentialModel(Base):
    __tablename__ = "user_credentials"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(
        String,
        ForeignKey("user_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    credential_type = mapped_column(SQLEnum(CredentialType), nullable=False)
    credential_identifier = mapped_column(String, nullable=False)  # e.g., hashed password, OAuth ID
    credential_secret = mapped_column(String, nullable=True)  # e.g., salt, refresh token
    is_verified = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used_at = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationship: many credentials belong to one user
    user = relationship("UserModel", back_populates="credentials")

    def __repr__(self):
        return f"<Credential(id={self.id}, type={self.credential_type})>"
