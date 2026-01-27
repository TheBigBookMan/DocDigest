import boto3
from utils import logs
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name = region_name)
        self.table_name = table_name
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    def get_item(self, session_id):
        self.logger.info(f"Retrieving item from DynamoDB: {session_id}")

        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={'session_id': {'S': session_id}},
                ProjectionExpression='status'
            )
            return self._deserialize_item(response['Item'])

        except Exception as e:
            self.logger.error(e)
            return False

    def update_row(self, session_id, update_query, update_values, updated_keys = {}):
        self.logger.info(f"Updating row for session {session_id}")

        try:
            return self.client.update_item(
                TableName=self.table_name,
                Key=self._serialize_item({'session_id': session_id}),
                UpdateExpression=update_query,
                ExpressionAttributeValues=self._serialize_item(update_values),
                ExpressionAttributeNames=updated_keys,
                ReturnValues="ALL_NEW"
            )

        except Exception as e:
            self.logger.error(e)
            return False

    def _serialize_item(self, data):
        """Convert Python dict to DynamoDB format"""
        return {key: self.serializer.serialize(value) for key, value in data.items()}

    def _deserialize_item(self, item):
        """Convert DynamoDB format to Python dict"""
        return {k: self.deserializer.deserialize(v) for k, v in item.items()}