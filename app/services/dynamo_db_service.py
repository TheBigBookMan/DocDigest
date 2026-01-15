import boto3
from utils import logs
from boto3.dynamodb.types import TypeSerializer

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name = region_name)
        self.table_name = table_name
        self.serializer = TypeSerializer()

    def check_table_exists(self):
        self.logger.info(f"Checking if table {self.table_name} exists")

        try:
            self.client.describe_table(TableName=self.table_name)
            self.logger.info(f"Table {self.table_name} exists")
            return True

        except Exception as e:
            self.logger.error(e)
            return False

    def insert_row(self, data):
        if not self.check_table_exists():
            return {
                'status': 'error',
                'message': 'Table does not exist'
            }

        try:
            self.client.put_item(TableName=self.table_name, Item=self._serialize_item(data))
            self.logger.info(f"Item added: {data}")
            return {
                'status': 'success'
            }

        except Exception as e:
            self.logger.error(e)
            return {
                'status': 'error',
                'message': 'Could not add item'
            }

    def _serialize_item(self, data):
        """Convert Python dict to DynamoDB format"""
        return {key: self.serializer.serialize(value) for key, value in data.items()}