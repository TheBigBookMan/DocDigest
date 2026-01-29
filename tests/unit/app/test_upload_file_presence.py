from unittest.mock import patch

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