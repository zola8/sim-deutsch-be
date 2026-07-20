from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .schema_enums import CredentialType


class UserProfileCredential(BaseModel):
    id: Optional[int] = None
    user_id: str
    credential_type: CredentialType
    credential_identifier: str  # hashed password, Google OAuth ID
    credential_secret: Optional[str] = None  # salt, refresh token
    is_verified: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_used_at: Optional[str] = None
