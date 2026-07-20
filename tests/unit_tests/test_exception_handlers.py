class TestUserNotFoundHandler:
    def test_returns_404_with_details(self, test_app):
        response = test_app.get("/trigger/not-found")
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "USER_NOT_FOUND"
        assert body["details"]["user_id"] == "missing-id"

    def test_handles_missing_user_id(self, test_app):
        response = test_app.get("/trigger/not-found-no-id")
        assert response.status_code == 404
        body = response.json()
        assert body["details"] is None


class TestUserAlreadyExistsHandler:
    def test_returns_409_with_field(self, test_app):
        response = test_app.get("/trigger/already-exists")
        assert response.status_code == 409
        body = response.json()
        assert body["error_code"] == "USER_ALREADY_EXISTS"
        assert body["details"]["field"] == "email"


class TestValidationHandler:
    def test_returns_422_with_field_details(self, test_app):
        # Send invalid payload: bad email, missing age
        response = test_app.post("/trigger/validation", json={"email": "not-an-email"})
        assert response.status_code == 422
        body = response.json()
        assert body["error_code"] == "VALIDATION_ERROR"
        assert isinstance(body["details"], list)
        assert len(body["details"]) >= 1
        # Each detail should have 'field' and 'message'
        for detail in body["details"]:
            assert "field" in detail
            assert "message" in detail


class TestGlobalFallbackHandler:
    def test_returns_500_and_hides_traceback(self, test_app):
        response = test_app.get("/trigger/unhandled")
        assert response.status_code == 500
        body = response.json()
        assert body["error_code"] == "INTERNAL_SERVER_ERROR"
        # Security: the actual RuntimeError message must NOT leak
        assert "terribly wrong" not in body["message"]
        assert body["details"] is None
