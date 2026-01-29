# DocDigest

DocDigest is a small webapp tool created for users to upload a document (pdf, doc, docx, txt) and the contents will be processed by an LLM to return a summary of the document.

## Features

- User uploads documents via a GUI on the web app
- The documents are processed via an LLM to provide a summary of the contents of the document
- The user is either notified via email of the completion with a zip containing the contents of the summaries
- The user can view in realtime the processing of the documents

## Architecture
The project consists of 3 different components.
- **Webapp**: A GUI for handling file upload and session management.
- **Processor Lambda**: Processes the files and extracts data using Claude API.
- **Notifier Lambda**: Sends completion email with the extracted data from files.

Event-driven architecture using AWS services (S3, SQS, SNS, DynamoDB, SES, Lambda)

ADRs in `/documentation`
```mermaid
flowchart TD;
    client[Client Browser] -->|HTTP POST| api[Flask API];
    api -->|1. Upload files| s3_bucket[S3 Bucket];
    api -->|2. Store session data| dynamo_db[DynamoDB]
    api -->|3. Response `Processing upload` or `Error`| client;

    s3_bucket -->|4. Event| sqs_service[SQS Service];
    sqs_service -->|5. Trigger| processing_lambda[Processor Lambda];
    processing_lambda -->|6. Check row exists| dynamo_db;
    processing_lambda -->|7. Retrieves file| s3_bucket;
    processing_lambda -->|8. Scrape| llm[LLM];
    processing_lambda -->|9. Update results| dynamo_db;
    processing_lambda -->|10. Delete file from S3| s3_bucket;
    processing_lambda -->|11. All files done?| check{Check Count};
    check -- Yes --> sns[SNS Topic];
    sns -->|12. Triggers| notifier_lambda[Notifier Lambda];
    notifier_lambda -->|13. Get all data| dynamo_db;
    notifier_lambda -->|14. Send email| ses[AWS SES];
    ses --> user[User Inbox];
```

## Quick Start

### Prerequisites

- AWS account with appropriate permissions
- Python 3.11+
- Docker

### Local Development
Clone the repo
```bash
git clone https://github.com/TheBigBookMan/DocDigest.git
cd docdigest
```

### Environment Setup
Setup the virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate
```

### Installation
Install correct dependencies
```bash
pip install -r requirements.txt
```

### Configuration
Setup the environment variables

#### Webapp
```bash
cp app/.env.example app/.env
cp .flaskenv.example .flaskenv
```

app/.env
```
ENVIRONMENT='development'

AWS_ACCESS_KEY_ID=access_key_id_for_iam
AWS_SECRET_ACCESS_KEY=secret_secret_key
AWS_DEFAULT_REGION=aws_region
S3_BUCKET=bucket_name
DYNAMO_DB_TABLE=dynamo_table_name
```

.flaskenv
```
FLASK_APP=app/app.py // points flask to look for where app starts
FLASK_DEBUG=1 // this turns on debug mode for hot reloading in flask
```

#### Processor Lambda
```bash
cp lambda/processor/.env.example lambda/processor/.env
```

lambda/processor/.env
```
AWS_ACCESS_KEY_ID=aws_access_key_id
AWS_SECRET_ACCESS_KEY=aws_secret_access_key
AWS_DEFAULT_REGION=aws_region
S3_BUCKET=bucket_name
ANTHROPIC_API_KEY=anthropic_api_key
DYNAMO_DB_TABLE=dynamo_table
SNS_TOPIC_ARN=sns_topic_arn
```

#### Notifier Lambda
```bash
cp lambda/notifier/.env.example lambda/notifier/.env
```

lambda/notifier/.env
```
AWS_ACCESS_KEY_ID=aws_access_key
AWS_SECRET_ACCESS_KEY=aws_secret_access_key
AWS_DEFAULT_REGION=aws_region
DYNAMO_DB_TABLE=dynamo_table
SES_EMAIL_SOURCE=ses_email_source
```

### Start
Start the flask webapp locally at `http://127.0.0.1:5000`
```bash
flask run
```

## Development

### Running Tests

How to run the test suite.

### Local Development

How to run locally without deploying to AWS.

## Deployment

How to deploy to AWS (ideally one command).

## Cost Estimation

What this costs to run at various scales.

## License

MIT or whatever you choose.