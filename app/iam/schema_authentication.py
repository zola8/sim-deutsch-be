from pydantic import BaseModel, EmailStr, model_validator

from .schema_enums import UserStatus, MIN_USERNAME_LENGTH, MAX_USERNAME_LENGTH, MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from .schema_user_profile import UserProfile


class RegisterWithPasswordRequest(BaseModel):
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
            raise ValueError('Password length should be between 8-20 characters')
        return self

    @model_validator(mode='after')
    def check_username_length(self):
        if len(self.username) < MIN_USERNAME_LENGTH or len(self.username) > MAX_USERNAME_LENGTH:
            raise ValueError('Username should be between 5-100 characters')
        return self


class RegisterResponse(BaseModel):
    user_id: str
    status: UserStatus
    message: str = "Registration successful"


class LoginWithPasswordRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
