import pytest
from unittest.mock import Mock
from io import BytesIO

@pytest.fixture
def client():
    """Flask test client."""
    from app import app

    app.config.update(TESTING=True)

    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_config():
    """Mock config object."""
    mock = Mock()
    mock.S3_BUCKET_NAME = 'test_bucket'
    mock.AWS_DEFAULT_REGION = 'us-east-1'
    mock.DYNAMO_DB_TABLE = 'test_table'
    return mock

@pytest.fixture
def sample_file():
    """Create a sample PDF file for testing."""
    return (BytesIO(b'fake pdf content'), 'invoice.pdf')