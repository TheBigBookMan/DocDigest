import boto3
import logging

class S3Service:
    def __init__(self, bucket_name, s3_region):
        self.bucket_name = bucket_name.lower()
        self.client = boto3.client('s3', region_name=s3_region)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def check_bucket_exists(self):
        self.logger.info(f"Checking if bucket {self.bucket_name} exists")

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Bucket {self.bucket_name} exists")
            return True

        except Exception as e:
            self.logger.error(e)
            return False

    def retrieve_file_from_s3(self, key):
        path_name = self.bucket_name + "/" + key
        self.logger.info(f"Retrieving {path_name} from s3")

        try:
            uploaded_file = self.client.get_object(Bucket=self.bucket_name, Key=key)
            return {
                'status': 'success',
                'data': uploaded_file
            }

        except Exception as e:
            self.logger.error(e)
            return False
