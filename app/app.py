import os

from flask import Flask, render_template, request
from helpers import functions, s3, dynamo_db
from dotenv import load_dotenv
from utils import logs

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

    if len(files) < 1:
        return {
            'status': 'error',
            'message': 'Files need to be uploaded'
        }

    cannot_process = []
    files_to_process = []

    for file in files:
        if not functions.allowed_file(file.filename):
            cannot_process.append({
                'filename': file.filename,
                'reason': 'Not correct format'
            })

        files_to_process.append(file)

    if len(cannot_process) == len(files):
        return {
            'status': 'error',
            'message': 'All files format not accepted',
            'cannot_process': cannot_process
        }

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
        upload_response = s3.upload_file_to_s3(file, bucket_name, file.filename)

        if upload_response:
            uploaded_files.append(file.filename)

    if len(uploaded_files) == 0:
        return {
            'status': 'error',
            'message': 'No uploaded files'
        }

    return {
        'status': 'success',
        'message': 'Processing...',
        'uploaded_files': uploaded_files,
    }

