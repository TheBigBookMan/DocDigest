import os

from flask import Flask, render_template, request
from helpers import functions, s3
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload_file.html')

@app.route('/upload', methods=['POST'])
def upload():

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
    print(files)

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

    for file in files_to_process:
        upload_response = s3.upload_file_to_s3(file, os.getenv('S3_BUCKET'), file.filename)




    return {
        'status': 'success',
        'message': 'Processing...',
        'cannot_process': cannot_process
    }

