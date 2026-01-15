import boto3
import os
import logging
from dotenv import load_dotenv
from services.s3_service import S3Service

load_dotenv()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Starting lambda handler")

    s3_handler = S3Service(os.getenv('S3_BUCKET'), os.getenv('AWS_DEFAULT_REGION'))

    if not s3_handler.check_bucket_exists():
        return {
            'status': 'error',
            'message': 'S3 bucket does not exist'
        }

    # TODO retrieve file from S3

