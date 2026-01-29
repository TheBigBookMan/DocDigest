
class TestUploadMethodValidation:
    """Unit tests for HTTP method validation."""

    def test_get_request_not_allowed(self, client):
        """Get request not allowed."""
        response = client.get('/upload')
        assert response.status_code == 405

