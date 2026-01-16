import boto3
import os
import logging
from dotenv import load_dotenv
from services import S3Service, ClaudeService
from helper import parse_lambda, extract_text_from_pdf
from claude_prompts import system_prompt

load_dotenv()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Starting lambda handler")

    # Get s3 and SQS information from event
    s3_event_data = parse_lambda(event)
    s3_object_data = s3_event_data['s3']
    logger.info(f"Time: {s3_event_data['event_time']}: Received event: {s3_event_data['event_source']} with action {s3_event_data['event_name']}")

    s3_handler = S3Service(os.getenv('S3_BUCKET'), os.getenv('AWS_DEFAULT_REGION'))

    if not s3_handler.check_bucket_exists():
        return {
            'status': 'error',
            'message': 'S3 bucket does not exist'
        }

    # Retrieve file from s3
    uploaded_file = s3_handler.retrieve_file_from_s3(s3_object_data['object']['key'])

    if not uploaded_file:
        return {
            'status': 'error',
            'message': 'File does not exist'
        }

    file_data = uploaded_file['data']

    if file_data['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'status': 'error',
            'message': 'Error retrieving file'
        }

    file_body = file_data['Body'].read()
    parsed_file_body = extract_text_from_pdf(file_body)

    # Query claude with file
    claude_handler = ClaudeService(os.getenv('ANTHROPIC_API_KEY'))

    if not claude_handler:
        return {
            'status': 'error',
            'message': 'Error retrieving claude'
        }

    claude_prompt = "Extract structured data from this invoice/receipt: " + parsed_file_body
    claude_response = claude_handler.query_claude(claude_prompt, system_prompt)

    if not claude_response:
        return {
            'status': 'error',
            'message': 'Error retrieving claude'
        }



    # TODO update response of the DynamoDB record and number completed
    # TODO check if every file is completed
    #       TODO if yes then send off SNS notifier to notifier lambda

# TODO if all is completed, then delete files from bucket? can say thats security decision???


if __name__ == '__main__':
    print("heree")
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy...",
                "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"ap-southeast-2\",\"eventTime\":\"2026-01-15T14:30:45.123Z\",\"eventName\":\"ObjectCreated:Put\",\"s3\":{\"bucket\":{\"name\":\"docdigest\"},\"object\":{\"key\":\"9132b141-de57-4e55-9d75-36aca9616c9a/invoice_sample.pdf\",\"size\":2048576}}}]}",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1705327845123",
                    "SenderId": "AIDAIT2UOQQY3AUEKVGXU",
                    "ApproximateFirstReceiveTimestamp": "1705327845128"
                },
                "messageAttributes": {},
                "md5OfBody": "098f6bcd4621d373cade4e832627b4f6",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:ap-southeast-2:123456789:docdigest-processing-queue",
                "awsRegion": "ap-southeast-2"
            }
        ]
    }
    context = {}
    lambda_handler(event, context)