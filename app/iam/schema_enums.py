from enum import Enum

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 20
MIN_USERNAME_LENGTH = 5
MAX_USERNAME_LENGTH = 100


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class CredentialType(str, Enum):
    PASSWORD = "password"
    OPENID_GOOGLE = "openid_google"  # "Login with Google"
