import json

def parse_lambda(event):
    event_body = event['Records'][0]['body']
    s3_event = json.loads(event_body)
    event_records = s3_event['Records'][0]

    return {
        'event_source': event_records['eventSource'],
        'event_time': event_records['eventTime'],
        'event_name': event_records['eventName'],
        's3': event_records['s3'],
    }