import boto3
import config
from utils import logs
from helper import parse_lambda, build_html_email
from services import DynamoDBService, SNSService

logger = logs.get_logger('lambda-notifier')

def lambda_handler(event, context):
    logger.info("Starting lambda-notifier handler")

    # Get event information
    lambda_event_data = parse_lambda(event)

    logger.info(f"Time: {lambda_event_data['event_time']}: Received event: {lambda_event_data['event_source']} with action {lambda_event_data['event_type']}")

    session_id = lambda_event_data['event_message']['session_id']

    config_handler = config.Config()

    # Get dynamodb record
    dynamo_handler = DynamoDBService(config_handler.AWS_DEFAULT_REGION, config_handler.DYNAMO_DB_TABLE)

    retrieved_item = dynamo_handler.get_item(session_id)

    if not retrieved_item:
        return {
            'status': 'error',
            'message': 'Could not retrieve item from DynamoDB'
        }

    item_data = retrieved_item

    if item_data['status'] != 'COMPLETED':
        logger.error(f"Item has not completed processing")
        return {
            'status': 'error',
            'message': 'Item not completed processing'
        }

    # Format the information into email
    prepared_email = build_html_email(item_data)

    print(prepared_email)



# TODO send SES


if __name__ == '__main__':
    print("Testing lambda notiofier")

    event = {
      "Records": [
        {
          "EventVersion": "1.0",
          "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:sns-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
          "EventSource": "aws:sns",
          "Sns": {
            "SignatureVersion": "1",
            "Timestamp": "2019-01-02T12:45:07.000Z",
            "Signature": "tcc6faL2yUC6dgZdmrwh1Y4cGa/ebXEkAi6RibDsvpi+tE/1+82j...65r==",
            "SigningCertURL": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-ac565b8b1a6c5d002d285f9598aa1d9b.pem",
            "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
            "Message": "{\"event_type\":\"session_complete\",\"session_id\":\"e54a22c5-0634-4a90-8aeb-e25ec3df1701\",\"email\":\"bjsmerd@gmail.com\",\"total_files\":3,\"completed_at\":\"2026-01-22T14:30:45.123Z\",\"uploaded_at\":\"2026-01-22T14:29:30.000Z\"}",
            "MessageAttributes": {
              "Test": {
                "Type": "String",
                "Value": "TestString"
              },
              "TestBinary": {
                "Type": "Binary",
                "Value": "TestBinary"
              }
            },
            "Type": "Notification",
            "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&amp;SubscriptionArn=arn:aws:sns:us-east-1:123456789012:test-lambda:21be56ed-a058-49f5-8c98-aedd2564c486",
            "TopicArn":"arn:aws:sns:us-east-1:123456789012:sns-lambda",
            "Subject": "TestInvoke"
          }
        }
      ]
    }
    context = {}
    lambda_handler(event, context)