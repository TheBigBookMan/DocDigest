import boto3
from utils import logs

dynamo_db = boto3.client('dynamodb')
logger = logs.get_logger('dynamo_db')

def check_table_exists(name):
    logger.info(f"Checking if table {name} exists")
    try:
        dynamo_db.describe_table(TableName=name)
        logger.info(f"Table {name} exists")
        return True
    except Exception as e:
        logger.error(e)
        return False
