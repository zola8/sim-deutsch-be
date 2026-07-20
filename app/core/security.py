# app/core/security.py

import logging

import bcrypt

logger = logging.getLogger(__name__)


class PasswordHasher:
    """Handles password hashing and verification using bcrypt."""

    def hash(self, password: str) -> str:
        """Hash a password. Returns the hash as a string."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    def verify(self, password: str, hashed_password: str) -> bool:
        """Verify a password against a hash. Returns True if match."""
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, TypeError) as e:
            logger.warning(f"Password verification failed due to invalid hash format: {e}")
            return False
