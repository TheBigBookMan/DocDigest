from unittest.mock import patch, Mock

class TestUploadFilePresence:
    """Unit test for the file validation"""

    def test_upload_file_presence(self, client):
        """Request without files in POST request should fail"""
        response = client.post('/upload', data={
            'email': 'test@gmail.com'
        })

        assert response.status_code == 400

        json_data = response.get_json()
        assert json_data['status'] == 'error'
        assert 'Files need to be uploaded' in json_data['message']

    @patch('app.file_validation.validate')
    def test_validation_error_returned(self, mock_validation, client, sample_file):
        """If file field passed in POST request but then fails validate(), endpoint return error message"""

        mock_validation.return_value = {
            'status': 'error',
            'message': 'Files need to be uploaded'
        }

        response = client.post('/upload',
            data={
                'email': 'test@gmail.com',
                'files': [sample_file]
            },
            content_type='multipart/form-data'
        )

        json_data = response.get_json()
        assert json_data['status'] == 'error'
        assert response.status_code == 400

        mock_validation.assert_called_once()

    @patch('app.config.Config')
    @patch('app.S3Service')
    @patch('app.file_validation.validate')
    def test_validation_success_returned(self, mock_validation, mock_s3_class, mock_config_class, client, sample_file):
        """If field passed in POST request and then passes validate(), processing continue and error at S3 bucket check"""

        mock_validation.return_value = {
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
        mock_s3_instance.check_bucket_exists.return_value = False
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
        assert 'S3 bucket does not exist' in json_data['message']

        mock_validation.assert_called_once()
        mock_config_class.assert_called_once()
        mock_s3_class.assert_called_once_with('test-bucket', 'test-region')
        mock_s3_instance.check_bucket_exists.assert_called_once()