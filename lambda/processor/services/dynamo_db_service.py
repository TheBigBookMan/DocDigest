import boto3
from utils import logs

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name = region_name)
        self.table_name = table_name

    def update_row(self, session_id, update_query, update_values, updated_keys):
        self.logger.info(f"Updating row for session {session_id}")

        try:
            return self.client.update_item(
                TableName=self.table_name,
                Key=session_id,
                UpdateExpression=update_query,
                ExpressionAttributeValues=update_values,
                ExpressionAttributeNames=updated_keys,
                ReturnValues="UPDATED_NEW"
            )

        except Exception as e:
            self.logger.error(e)
            return False