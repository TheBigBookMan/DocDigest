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

def create_item(table_name, data):
    logger.info(f"Inserting into table: {table_name}")

    try:
        dynamo_db.put_item(TableName=table_name, Item=data)
        logger.info(f"Item added: {data}")
        return True

    except Exception as e:
        logger.error(e)
        return False