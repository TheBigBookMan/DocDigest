import boto3
from utils import logs

class SESService:
    def __init__(self, region_name):
        self.logger = logs.get_logger('ses')
        self.client = boto3.client('ses', region_name=region_name)

    def send_email(self, email_info):
        ...

