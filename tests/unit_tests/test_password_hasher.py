class TestPasswordHasher:
    def test_hash_returns_string(self, hasher):
        result = hasher.hash("mypassword")
        assert isinstance(result, str)

    def test_hash_starts_with_bcrypt_prefix(self, hasher):
        result = hasher.hash("mypassword")
        assert result.startswith("$2b$")

    def test_hash_is_different_each_time(self, hasher):
        # Different salts should produce different hashes
        hash1 = hasher.hash("samepassword")
        hash2 = hasher.hash("samepassword")
        assert hash1 != hash2

    def test_verify_correct_password(self, hasher):
        hashed = hasher.hash("mypassword")
        assert hasher.verify("mypassword", hashed) is True

    def test_verify_wrong_password(self, hasher):
        hashed = hasher.hash("mypassword")
        assert hasher.verify("wrongpassword", hashed) is False

    def test_verify_handles_invalid_hash_gracefully(self, hasher):
        # Should not raise, just return False
        assert hasher.verify("password", "not-a-valid-hash") is False
        assert hasher.verify("password", "") is False

    def test_verify_handles_unicode_passwords(self, hasher):
        hashed = hasher.hash("пароль密码🔐")
        assert hasher.verify("пароль密码🔐", hashed) is True
        assert hasher.verify("wrong", hashed) is False
