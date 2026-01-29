
class TestHomePage:
    """Unit test for HTTP method validation."""

    def test_get_request_allowed(self, client):
        """GET request should be allowed."""
        response = client.get('/')
        assert response.status_code == 200

    def test_home_page_renders_template(self, client):
        """Home page should render html template"""
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        assert len(response.data) > 0