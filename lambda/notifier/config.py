import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    ENVIRONMENT = os.getenv('ENVIRONMENT')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
    DYNAMO_DB_TABLE = os.getenv('DYNAMO_DB_TABLE')