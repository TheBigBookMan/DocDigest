import json

def parse_lambda(event):
    event_body = event['Records'][0]
    sns_event = event_body['Sns']

    return {
        'event_source': event_body['EventSource'],
        'event_time': sns_event['Timestamp'],
        'event_type': sns_event['Type'],
        'event_message': sns_event['Message'],
    }