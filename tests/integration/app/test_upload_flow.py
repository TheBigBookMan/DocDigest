# tests/integration/test_upload_flow.py

import pytest
from unittest.mock import patch, Mock
from io import BytesIO
from moto import mock_s3, mock_dynamodb
import boto3


@pytest.fixture
def client():
    """Flask test client"""
    from app import app
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_pdf_file():
    """Valid PDF file for testing"""
    return (BytesIO(b'%PDF-1.4 fake pdf content'), 'invoice.pdf')


@pytest.fixture
def invalid_image_file():
    """Invalid image file for testing"""
    return (BytesIO(b'fake jpg content'), 'photo.jpg')


class TestUploadFlowIntegration:
    """Integration tests for upload flow with real components"""

    @mock_s3
    @mock_dynamodb
    @patch('app.config.Config')
    def test_complete_successful_upload_flow(
            self,
            mock_config_class,
            client,
            valid_pdf_file
    ):
        """
        Test complete upload flow with real validation and service classes
        Only AWS is mocked (using moto)
        """

        # Setup mock config
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'us-west-2'
        mock_config.DYNAMO_DB_TABLE = 'test-table'
        mock_config_class.return_value = mock_config

        # Setup real S3 bucket (mocked with moto)
        s3 = boto3.client('s3', region_name='us-west-2')
        s3.create_bucket(
            Bucket='test-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )

        # Setup real DynamoDB table (mocked with moto)
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[
                {'AttributeName': 'session_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'session_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Make upload request
        # This uses REAL file_validation.validate()
        # This uses REAL S3Service (but S3 is mocked)
        # This uses REAL DynamoDBService (but DynamoDB is mocked)
        response = client.post('/upload',
                               data={
                                   'email': 'user@example.com',
                                   'files': [valid_pdf_file]
                               },
                               content_type='multipart/form-data'
                               )

        json_data = response.get_json()

        # ===== Verify Response =====
        assert response.status_code == 200
        assert json_data['status'] == 'success'
        assert json_data['message'] == 'Processing...'
        assert len(json_data['uploaded_files']) > 0

        session_id = json_data['session_id']

        # ===== Verify file actually uploaded to S3 =====
        objects = s3.list_objects_v2(Bucket='test-bucket', Prefix=f'{session_id}/')
        assert objects['KeyCount'] == 1  # File exists in S3

        uploaded_key = objects['Contents'][0]['Key']
        assert session_id in uploaded_key
        assert 'invoice.pdf' in uploaded_key

        # ===== Verify session created in DynamoDB =====
        db_session = table.get_item(Key={'session_id': session_id})['Item']

        assert db_session['session_id'] == session_id
        assert db_session['email'] == 'user@example.com'
        assert db_session['total_files'] == 1
        assert db_session['completed_count'] == 0
        assert db_session['status'] == 'PROCESSING'
        assert 'uploaded_at' in db_session
        assert db_session['completed_at'] is None

    @mock_s3
    @mock_dynamodb
    @patch('app.config.Config')
    def test_invalid_file_rejected_by_real_validation(
            self,
            mock_config_class,
            client,
            invalid_image_file
    ):
        """
        Test that real file_validation.validate() rejects invalid files
        This uses REAL validation logic, not mocked
        """

        # Setup config
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'us-west-2'
        mock_config.DYNAMO_DB_TABLE = 'test-table'
        mock_config_class.return_value = mock_config

        # Setup AWS (even though we shouldn't reach them)
        s3 = boto3.client('s3', region_name='us-west-2')
        s3.create_bucket(
            Bucket='test-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )

        # Upload invalid file
        response = client.post('/upload',
                               data={
                                   'email': 'user@example.com',
                                   'files': [invalid_image_file]
                               },
                               content_type='multipart/form-data'
                               )

        json_data = response.get_json()

        # Should be rejected by REAL validation
        assert response.status_code == 400
        assert json_data['status'] == 'error'
        assert 'format not accepted' in json_data['message'].lower()

        # Nothing uploaded to S3
        objects = s3.list_objects_v2(Bucket='test-bucket')
        assert objects.get('KeyCount', 0) == 0

    @mock_s3
    @mock_dynamodb
    @patch('app.config.Config')
    def test_multiple_files_upload_and_track_correctly(
            self,
            mock_config_class,
            client,
            valid_pdf_file
    ):
        """Test uploading multiple files creates correct DynamoDB entry"""

        # Setup
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'us-west-2'
        mock_config.DYNAMO_DB_TABLE = 'test-table'
        mock_config_class.return_value = mock_config

        # Setup AWS
        s3 = boto3.client('s3', region_name='us-west-2')
        s3.create_bucket(
            Bucket='test-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )

        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.create_table(
            TableName='test-table',
            KeySchema=[{'AttributeName': 'session_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'session_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create 3 files
        file1 = (BytesIO(b'%PDF-1.4 file1'), 'invoice1.pdf')
        file2 = (BytesIO(b'%PDF-1.4 file2'), 'invoice2.pdf')
        file3 = (BytesIO(b'%PDF-1.4 file3'), 'invoice3.pdf')

        # Upload
        response = client.post('/upload',
                               data={
                                   'email': 'user@example.com',
                                   'files': [file1, file2, file3]
                               },
                               content_type='multipart/form-data'
                               )

        json_data = response.get_json()
        session_id = json_data['session_id']

        # Verify 3 files in S3
        objects = s3.list_objects_v2(Bucket='test-bucket', Prefix=f'{session_id}/')
        assert objects['KeyCount'] == 3

        # Verify DynamoDB has total_files = 3
        db_session = table.get_item(Key={'session_id': session_id})['Item']
        assert db_session['total_files'] == 3
        assert db_session['completed_count'] == 0

    @mock_s3
    @patch('app.config.Config')
    def test_s3_bucket_missing_returns_error(
            self,
            mock_config_class,
            client,
            valid_pdf_file
    ):
        """Test error when S3 bucket doesn't exist (real S3Service check)"""

        # Setup config pointing to non-existent bucket
        mock_config = Mock()
        mock_config.S3_BUCKET = 'non-existent-bucket'
        mock_config.AWS_DEFAULT_REGION = 'us-west-2'
        mock_config_class.return_value = mock_config

        # Don't create the bucket

        # Upload
        response = client.post('/upload',
                               data={
                                   'email': 'user@example.com',
                                   'files': [valid_pdf_file]
                               },
                               content_type='multipart/form-data'
                               )

        json_data = response.get_json()

        # Should fail at S3 bucket check
        assert response.status_code == 500
        assert json_data['status'] == 'error'
        assert 'bucket does not exist' in json_data['message'].lower()