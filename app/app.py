import os
import uuid
import datetime

from flask import Flask, render_template, request
from helpers import functions, s3, dynamo_db
from dotenv import load_dotenv
from utils import logs
from components import file_validation

load_dotenv()
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

    bucket_name = os.getenv('S3_BUCKET')
    bucket_exists = s3.check_bucket_exists(bucket_name)

    if not bucket_exists:
        return {
            'status': 'error',
            'message': 'S3 bucket does not exist'
        }

    table_name = os.getenv('DYNAMO_DB_TABLE')
    table_exists = dynamo_db.check_table_exists(table_name)

    if not table_exists:
        return {
            'status': 'error',
            'message': 'DynamoDB table does not exist'
        }

    uploaded_files = []

    for file in files_to_process:
        upload_response = s3.upload_file_to_s3(file, bucket_name, f"{session_id}/{file.filename}")

        if upload_response:
            uploaded_files.append(file.filename)

    if len(uploaded_files) == 0:
        return {
            'status': 'error',
            'message': 'No uploaded files'
        }

    payload = {
        'session_id': session_id,
        'email': email,
        'total_files': len(uploaded_files),
        'completed_files': '0',
        'uploaded_time': datetime.now(),
        'response': []
    }

    insert_dynamo = dynamo_db.create_item(table_name, payload)

    if not insert_dynamo:
        return {
            'status': 'error',
            'message': 'DynamoDB error'
        }



    return {
        'status': 'success',
        'message': 'Processing...',
        'uploaded_files': uploaded_files,
    }

