from unittest.mock import patch, Mock

class TestUploadS3File:
    """Tests for the S3Service inserting s3 file"""

    @patch('app.file_validation.validate')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_s3_insert_fail(self, mock_s3_class, mock_config_class, mock_validate, client, sample_file):
        """S3 insert fails"""

        mock_validate.return_value = {
            'status': 'success',
            'files': [sample_file, sample_file]
        }

        # Mock config setup
        mock_config = Mock()
        mock_config.S3_BUCKET = 'test-bucket'
        mock_config.AWS_DEFAULT_REGION = 'test-region'
        mock_config_class.return_value = mock_config

        # Mock S3 service
        mock_s3_instance = Mock()
        mock_s3_instance.check_bucket_exists.return_value = True
        mock_s3_instance.insert_s3.return_value = {
            'status': 'error',
            'message': 'No uploaded files'
        }
        mock_s3_class.return_value = mock_s3_instance

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
        assert 'No uploaded files' in json_data['message']

        mock_s3_instance.insert_s3.assert_called_once()

    @patch('app.file_validation.validate')
    @patch('app.DynamoDBService')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_s3_insert_success(self, mock_s3_class, mock_config_class, mock_dynamo_class, mock_validate, client, sample_file):
        """S3 insert success and then fail at dynamodb row insert to show S3 was successful"""

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
            'uploaded_files': [sample_file, sample_file]
        }
        mock_s3_class.return_value = mock_s3_instance

        # Mock Dynamo service- this is where the error occurs as it indicates that the S3 insert was successful to get to the dynamo insert section
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

        mock_s3_instance.insert_s3.assert_called_once()
        mock_dynamo_instance.insert_row.assert_called_once()