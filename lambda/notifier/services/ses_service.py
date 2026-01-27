import boto3
from utils import logs

class SESService:
    def __init__(self, region_name):
        self.logger = logs.get_logger('ses')
        self.client = boto3.client('ses', region_name=region_name)

    def send_email(self, email_source, email_destination, prepared_email_html):
        self.logger.info(f"Sending email")

        try:
            return self.client.send_email({
                'Source': email_source,
                'Destination': {
                    'ToAddresses': [
                        email_destination
                    ]
                },
                'Message': {
                    'Subject': {
                        'Data': 'DocDigest summary of the uploaded files.'
                    },
                    'Body': {
                        'Html': {
                            'Data': prepared_email_html
                        }
                    }
                },
            })

        except Exception as e:
            self.logger.error(e)
            return False