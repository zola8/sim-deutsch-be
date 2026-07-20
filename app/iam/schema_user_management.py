from typing import List, Optional

from pydantic import BaseModel, EmailStr, model_validator

from app.iam.schema_enums import MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, UserStatus


class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    roles: List[str] = ["USER"]

    @model_validator(mode='after')
    def check_username_length(self):
        if len(self.username) < MIN_USERNAME_LENGTH or len(self.username) > MAX_USERNAME_LENGTH:
            raise ValueError('Username should be between 5-100 characters')
        return self


class UserCreateResponse(BaseModel):
    user_id: str
    status: UserStatus


class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    status: Optional[UserStatus] = None
    roles: Optional[List[str]] = None

    @model_validator(mode='after')
    def check_username_length(self):
        if self.username and (len(self.username) < MIN_USERNAME_LENGTH or len(self.username) > MAX_USERNAME_LENGTH):
            raise ValueError('Username should be between 5-100 characters')
        return self
