import boto3
import config
from utils import logs
from services import S3Service, ClaudeService, DynamoDBService
from helper import parse_lambda, extract_text_from_pdf
from claude_prompts import system_prompt

logger = logs.get_logger('lambda')

def lambda_handler(event, context):
    logger.info(f"Starting lambda handler")

    # Get s3 and SQS information from event
    s3_event_data = parse_lambda(event)
    s3_object_data = s3_event_data['s3']
    logger.info(f"Time: {s3_event_data['event_time']}: Received event: {s3_event_data['event_source']} with action {s3_event_data['event_name']}")

    s3_key = s3_object_data['object']['key']
    s3_key_vals = s3_key.split('/')
    session_id = s3_key_vals[0]
    filename = s3_key_vals[1]

    config_handler = config.Config()

    # TODO documentation checking at start to ensure not already processed
    dynamo_handler = DynamoDBService(config_handler.AWS_DEFAULT_REGION, config_handler.DYNAMO_DB_TABLE)

    # Check row in dynamo exists
    dynamo_row = dynamo_handler.get_item(session_id)

    if not dynamo_row:
        return {
            'status': 'error',
            'message': 'Error retrieving dynamo row'
        }

    if dynamo_row['status'] == 'COMPLETED':
        return {
            'status': 'error',
            'message': 'Item already been processed'
        }

    s3_handler = S3Service(config_handler.S3_BUCKET, config_handler.AWS_DEFAULT_REGION)

    if not s3_handler.check_bucket_exists():
        return {
            'status': 'error',
            'message': 'S3 bucket does not exist'
        }

    # Retrieve file from s3
    uploaded_file = s3_handler.retrieve_file_from_s3(s3_key)

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
    claude_handler = ClaudeService(config_handler.ANTHROPIC_API_KEY)

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
    update_query = "ADD processed_files :f SET completed_count = completed_count + :inc, results.#filename = :output"
    updated_values = {
        ':f': {filename},
        ':inc': 1,
        ':output': claude_response
    }
    updated_keys = {
        '#filename': filename,
    }

    # Update dynamo row with results and updated tracking
    updated_row = dynamo_handler.update_row(session_id, update_query, updated_values, updated_keys)

    if not updated_row:
        return {
            'status': 'error',
            'message': 'Error updating dynamo table'
        }

    print(updated_row)

    if updated_row['Attributes']['completed_count'] >= updated_row['Attributes']['total_files']:
        ...
    #       TODO if yes then send off SNS notifier to notifier lambda
#           TODO update the row status to COMPLETED

    # TODO documentation on deleting the file after querying LLM for security
    # Delete file from S3 bucket for security
    deleted_file = s3_handler.delete_file_from_s3(s3_key)

    if not deleted_file:
        return {
            'status': 'error',
            'message': 'Error deleting file'
        }


if __name__ == '__main__':
    print("heree")
    event = {
        "Records": [
            {
                "messageId": "059f36b4-87a3-44ab-83d2-661975830a7d",
                "receiptHandle": "AQEBwJnKyrHigUMZj6rYigCgxlaS3SLy...",
                "body": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"ap-southeast-2\",\"eventTime\":\"2026-01-15T14:30:45.123Z\",\"eventName\":\"ObjectCreated:Put\",\"s3\":{\"bucket\":{\"name\":\"docdigest\"},\"object\":{\"key\":\"e54a22c5-0634-4a90-8aeb-e25ec3df1701/invoice_sample.pdf\",\"size\":2048576}}}]}",
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