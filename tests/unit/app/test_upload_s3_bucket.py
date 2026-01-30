from unittest.mock import Mock, patch

class TestUploadS3Bucket:
    """Testing the S3 bucket exists in the upload request"""

    @patch('app.file_validation.validate')
    @patch('app.config.Config')
    @patch('app.S3Service')
    def test_s3_bucket_exists(self, mock_s3_class, mock_config_class, mock_validate, client, sample_file):
        """If bucket exists, it should proceed to upload file step"""

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

        mock_s3_instance.check_bucket_exists.assert_called_once()
        mock_s3_instance.insert_s3.assert_called_once()