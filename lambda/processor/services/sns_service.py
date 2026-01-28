import boto3
from utils import logs

class SNSService:
    def __init__(self, default_region):
        self.logger = logs.get_logger('sns')
        self.client = boto3.client('sns', region_name=default_region)

    def publish_message(self, message, topic_arn):
        self.logger.info('Publishing message to SNS')

        try:
            return self.client.publish(
                TopicArn=topic_arn,
                Message=message,
                MessageStructure='json'
            )

        except Exception as e:
            self.logger.error(e)
            return False