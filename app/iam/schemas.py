from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, EmailStr, model_validator, Field


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_repeat: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_repeat:
            raise ValueError('Passwords do not match')
        return self

    @model_validator(mode='after')
    def check_passwords_is_not_empty(self):
        if not len(self.password) >= 8:
            raise ValueError('Passwords length should be at least 8 characters')
        return self


class UserCreateResponse(BaseModel):
    user_id: str
    status: UserStatus


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    status: UserStatus = UserStatus.INACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    # TODO  never return plain-text passwords!
    password: str
    roles: List[str]
