from datetime import datetime, timedelta, timezone

import jwt

from app.iam.exceptions import InvalidTokenError, TokenExpiredError


class TokenService:
    def __init__(self, secret_key: str, expire_minutes: int = 1440):  # 24 hours
        self.secret_key = secret_key
        self.expire_minutes = expire_minutes

    def generate_activation_token(self, user_id: str, credential_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        payload = {
            "sub": user_id,
            "cred_id": credential_id,
            "exp": expire,
            "type": "activation"
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_activation_token(self, token: str) -> tuple[str, int]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload.get("type") != "activation":
                raise InvalidTokenError("Invalid token type")
            return payload["sub"], int(payload["cred_id"])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Activation token has expired")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid activation token")
