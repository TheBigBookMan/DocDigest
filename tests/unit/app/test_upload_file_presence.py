
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

