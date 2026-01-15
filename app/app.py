import os
import uuid
import datetime

from flask import Flask, render_template, request
from utils import logs
from components import file_validation
from services import S3Service
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
    handle_s3 = s3_handler.insert_s3(session_id, files_to_process)

    if handle_s3['status'] == 'error':
        return handle_s3

    uploaded_files = handle_s3['uploaded_files']



    # table_name = os.getenv('DYNAMO_DB_TABLE')
    # table_exists = dynamo_db.check_table_exists(table_name)
    #
    # if not table_exists:
    #     return {
    #         'status': 'error',
    #         'message': 'DynamoDB table does not exist'
    #     }
    #
    # payload = {
    #     'session_id': session_id,
    #     'email': email,
    #     'total_files': len(uploaded_files),
    #     'completed_files': '0',
    #     'uploaded_time': datetime.now(),
    #     'response': []
    # }
    #
    # insert_dynamo = dynamo_db.create_item(table_name, payload)
    #
    # if not insert_dynamo:
    #     return {
    #         'status': 'error',
    #         'message': 'DynamoDB error'
    #     }
    #


    return {
        'status': 'success',
        'message': 'Processing...',
        'uploaded_files': uploaded_files,
    }

