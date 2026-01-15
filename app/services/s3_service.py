import boto3
from utils import logs

class S3Service:
    def __init__(self, bucket_name, s3_region):
        self.bucket_name = bucket_name.lower()
        self.client = boto3.client('s3', region_name=s3_region)
        self.logger = logs.get_logger('s3')

    def check_bucket_exists(self):
        self.logger.info(f"Checking if bucket {self.bucket_name} exists")

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Bucket {self.bucket_name} exists")
            return True

        except Exception as e:
            self.logger.error(e)
            return False

    def insert_s3(self, session_id, files):
        bucket_exists = self.check_bucket_exists()

        if not bucket_exists:
            self.logger.info(f"Bucket {self.bucket_name} does not exist")
            return {
                'status': 'error',
                'message': 'S3 bucket does not exist'
            }

        uploaded_files = []

        for file in files:
            upload_response = self.upload_file(file, f"{session_id}/{file.filename}")

            if upload_response:
                uploaded_files.append(file.filename)


        return {
            'status': 'success',
            'uploaded_files': uploaded_files
        }

    def upload_file(self, file, key):
        self.logger.info(f"Uploading to S3 bucket {self.bucket_name} and key {key}")

        try:
            self.client.upload_fileobj(file, self.bucket_name, key)
            self.logger.info(f"Successfully uploaded to S3 bucket {self.bucket_name} and key {key}")
            return True

        except Exception as e:
            self.logger.error(e)
            return False
