
class TestPageRenderValidation:
    """Unit test for HTTP method validation."""

    def test_get_request_allowed(self, client):
        """GET request should be allowed."""
        response = client.get('/')
        assert response.status_code == 200