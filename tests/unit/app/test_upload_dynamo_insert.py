from unittest.mock import patch, Mock

class TestUploadDynamoInsert:
    """Unit tests for the insert row in Dynamo DB"""

    @patch('app.file_validation.validate')
    @patch('app.DynamoDBService')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_insert_dynamo_fail_no_table(self, mock_s3_class, mock_config_class, mock_dynamo_class, mock_validate, client, sample_file):
        """Tests for the insert dynamo fail case- no table exist"""

        mock_validate.return_value = {
            'status': 'success',
            'files': [sample_file, sample_file]
        }

        # Mock config setup
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'test-region'
        mock_config.DYNAMODB_TABLE = 'test-dynamodb-table'
        mock_config_class.return_value = mock_config

        # Mock S3 service
        mock_s3_instance = Mock()
        mock_s3_instance.check_bucket_exists.return_value = True
        mock_s3_instance.insert_s3.return_value = {
            'status': 'success',
            'uploaded_files': ['invoice.pdf', 'test.pdf']
        }
        mock_s3_class.return_value = mock_s3_instance

        # Mock Dynamo service
        mock_dynamo_instance = Mock()
        mock_dynamo_instance.insert_row.return_value = {
            'status': 'error',
            'message': 'Table does not exist'
        }
        mock_dynamo_class.return_value = mock_dynamo_instance

        response = client.post('/upload',
            data={
                'email': 'test@gmail.com',
                'files': [sample_file, sample_file]
            },
            content_type='multipart/form-data'
        )
        json_data = response.get_json()

        assert response.status_code == 500
        assert json_data['status'] == 'error'
        assert 'Table does not exist' in json_data['message']

        mock_dynamo_instance.insert_row.assert_called_once()

    @patch('app.file_validation.validate')
    @patch('app.DynamoDBService')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_insert_dynamo_fail_error_insert(self, mock_s3_class, mock_config_class, mock_dynamo_class, mock_validate, client, sample_file):
        """Tests for the insert dynamo fail case- error uploading"""

        mock_validate.return_value = {
            'status': 'success',
            'files': [sample_file, sample_file]
        }

        # Mock config setup
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'test-region'
        mock_config.DYNAMODB_TABLE = 'test-dynamodb-table'
        mock_config_class.return_value = mock_config

        # Mock S3 service
        mock_s3_instance = Mock()
        mock_s3_instance.check_bucket_exists.return_value = True
        mock_s3_instance.insert_s3.return_value = {
            'status': 'success',
            'uploaded_files': ['invoice.pdf', 'test.pdf']
        }
        mock_s3_class.return_value = mock_s3_instance

        # Mock Dynamo service
        mock_dynamo_instance = Mock()
        mock_dynamo_instance.insert_row.return_value = {
            'status': 'error',
            'message': 'Could not add item'
        }
        mock_dynamo_class.return_value = mock_dynamo_instance

        response = client.post('/upload',
            data={
                'email': 'test@gmail.com',
                'files': [sample_file, sample_file]
            },
            content_type='multipart/form-data'
        )
        json_data = response.get_json()

        assert response.status_code == 500
        assert json_data['status'] == 'error'
        assert 'Could not add item' in json_data['message']

        mock_dynamo_instance.insert_row.assert_called_once()

    @patch('app.file_validation.validate')
    @patch('app.DynamoDBService')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_insert_dynamo_success(self, mock_s3_class, mock_config_class, mock_dynamo_class, mock_validate, client, sample_file):
        """Test for the insert DynamoDB row success case"""

        mock_validate.return_value = {
            'status': 'success',
            'files': [sample_file, sample_file]
        }

        # Mock config setup
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'test-region'
        mock_config.DYNAMODB_TABLE = 'test-dynamodb-table'
        mock_config_class.return_value = mock_config

        # Mock S3 service
        mock_s3_instance = Mock()
        mock_s3_instance.check_bucket_exists.return_value = True
        mock_s3_instance.insert_s3.return_value = {
            'status': 'success',
            'uploaded_files': ['invoice.pdf', 'test.pdf']
        }
        mock_s3_class.return_value = mock_s3_instance

        # Mock Dynamo service
        mock_dynamo_instance = Mock()
        mock_dynamo_instance.insert_row.return_value = {
            'status': 'success',
        }
        mock_dynamo_class.return_value = mock_dynamo_instance

        response = client.post('/upload',
            data={
                'email': 'test@gmail.com',
                'files': [sample_file, sample_file]
            },
            content_type='multipart/form-data'
        )
        json_data = response.get_json()

        assert response.status_code == 200
        assert json_data['status'] == 'success'
        assert 'Processing...' in json_data['message']
        assert json_data['uploaded_files'] == ['invoice.pdf', 'test.pdf']

        mock_dynamo_instance.insert_row.assert_called_once()