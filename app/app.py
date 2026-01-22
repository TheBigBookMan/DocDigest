import os
import uuid
import datetime

from flask import Flask, render_template, request
from utils import logs
from components import file_validation
from services import S3Service, DynamoDBService
import config

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload_file.html')

@app.route('/upload', methods=['POST'])
def upload():
    logger = logs.get_logger('app')
    logger.info("Uploading files...")

    if request.method != 'POST':
        return {
            'status': 'error',
            'message': 'Only POST method allowed'
        }

    if 'files' not in request.files:
        return {
            'status': 'error',
            'message': 'Files need to be uploaded'
        }

    files = request.files.getlist('files')
    email = request.form.get('email')
    session_id = str(uuid.uuid4())

    # Validate files are correct format
    validate_files = file_validation.validate(files)

    if validate_files['status'] == 'error':
        return validate_files

    files_to_process = validate_files['files']

    config_handler = config.Config()
    s3_handler = S3Service(config_handler.S3_BUCKET, config_handler.AWS_DEFAULT_REGION)

    # Handle uploading files to S3 bucket
    if not s3_handler.check_bucket_exists():
        return {
            'status': 'error',
            'message': 'S3 bucket does not exist'
        }

    upload_files_s3 = s3_handler.insert_s3(session_id, files_to_process)

    if upload_files_s3['status'] == 'error':
        return upload_files_s3

    uploaded_files = upload_files_s3['uploaded_files']

    dynamo_db_handler = DynamoDBService(config_handler.AWS_DEFAULT_REGION, config_handler.DYNAMO_DB_TABLE)

    # Handle inserting new row into DynamoDB
    payload = {
        'session_id': session_id,
        'email': email,
        'total_files': len(uploaded_files),
        'completed_count': 0,
        'processed_files': {'__INIT__'},
        'status': 'PROCESSING',
        'uploaded_at': datetime.datetime.now().isoformat(),
        'completed_at': None,
        'response': {}
    }

    # TODO add a TTL Time to live on the table so rows are deleted after X amount of tim
    # TODO write ADR about the time to live decicion
    insert_row_dynamo = dynamo_db_handler.insert_row(payload)

    if insert_row_dynamo['status'] == 'error':
        return insert_row_dynamo

    return {
        'status': 'success',
        'message': 'Processing...',
        'uploaded_files': uploaded_files,
    }