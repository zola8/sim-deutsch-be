from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, EmailStr, model_validator, Field

# Validation Rules
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 20
MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 100


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
    def check_password_length(self):
        if len(self.password) < MIN_PASSWORD_LENGTH or len(self.password) > MAX_PASSWORD_LENGTH:
            raise ValueError('Passwords length should be between 8-20 characters')
        return self

    @model_validator(mode='after')
    def check_username_length(self):
        if len(self.username) < MIN_USERNAME_LENGTH or len(self.username) > MAX_USERNAME_LENGTH:
            raise ValueError('Username should be between 5-100 characters')
        return self


class UserCreateResponse(BaseModel):
    user_id: str
    status: UserStatus


class UserUpdateRequest(BaseModel):
    username: str
    status: UserStatus = UserStatus.INACTIVE

    @model_validator(mode='after')
    def check_username_length(self):
        if len(self.username) < MIN_USERNAME_LENGTH or len(self.username) > MAX_USERNAME_LENGTH:
            raise ValueError('Username should be between 5-100 characters')
        return self


class UserProfile(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    status: UserStatus = UserStatus.INACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    # TODO  never return plain-text passwords!
    password: str
    roles: List[str]
