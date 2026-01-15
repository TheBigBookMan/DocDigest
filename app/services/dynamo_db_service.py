import boto3
from utils import logs

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name = region_name)
        self.table_name = table_name

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
            self.client.put_item(TableName=self.table_name, Item=data)
            self.logger.info(f"Item added: {data}")
            return True

        except Exception as e:
            self.logger.error(e)
            return {
                'status': 'error',
                'message': 'Could not add item'
            }