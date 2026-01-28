import boto3
from utils import logs

class SNSService:
    def __init__(self, default_region):
        self.logger = logs.get_logger('sns')
        self.client = boto3.client('sns', region_name=default_region)
