import boto3
from utils import logs

s3 = boto3.client('s3')
logger = logs.get_logger('s3')

def upload_file_to_s3(file_path, bucket, key):
    logger.info(f"Uploading to S3 bucket {bucket} and key {key}")

    try:
        s3.upload_fileobj(file_path, bucket, key)
        logger.info(f"Successfully uploaded to S3 bucket {bucket} and key {key}")
        return True

    except Exception as e:
        logger.error(e)
        return False

def check_bucket_exists(bucket_name):
    logger.info(f"Checking if bucket {bucket_name} exists")

    try:
        s3.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} exists")
        return True

    except Exception as e:
        logger.error(e)
        return False