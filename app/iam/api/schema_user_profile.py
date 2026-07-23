from typing import List

from pydantic import BaseModel, EmailStr

from app.iam.api.schema_enums import UserStatus


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    status: UserStatus = UserStatus.INACTIVE
    created_at: str
    roles: List[str] = ["USER"]
