from utils import logs
import boto3
from boto3.dynamodb.types import TypeDeserializer

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.table_name = table_name
        self.deserializer = TypeDeserializer()

    def get_item(self, session_id):
        self.logger.info(f"Getting item for session_id: {session_id}")

        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={'session_id': {'S': session_id}}
            )
            return self._deserialize_item(response['Item'])
        except Exception as e:
            self.logger.error(e)
            return False

    def _deserialize_item(self, item):
        """Convert DynamoDB format to Python dict"""
        return {k: self.deserializer.deserialize(v) for k, v in item.items()}