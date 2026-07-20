from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field

from app.iam.schema_enums import UserStatus


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    status: UserStatus = UserStatus.INACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    roles: List[str] = ["USER"]
