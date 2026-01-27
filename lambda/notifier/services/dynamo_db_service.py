from utils import logs
import boto3

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.table_name = table_name

    def get_item(self, session_id):
        self.logger.info(f"Getting item for session_id: {session_id}")

        try:
            return self.client.get_item(
                TableName=self.table_name,
                Key={'session_id': {'S': session_id}}
            )
        except Exception as e:
            self.logger.error(e)
            return False