from utils import logs
import boto3

class DynamoDBService:
    def __init__(self, region_name, table_name):
        self.logger = logs.get_logger('dynamodb')
        self.client = boto3.client('dynamodb', region_name=region_name)
        self.table_name = table_name

