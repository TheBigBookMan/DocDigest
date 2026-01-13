from flask import Flask, render_template, request
from helpers import functions

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

    for file in files:
        if not functions.allowed_file(file.filename):
            cannot_process.append({
                'filename': file.filename,
                'reason': 'Not correct format'
            })

    return {
        'status': 'success',
        'message': 'Processing...',
        'cannot_process': cannot_process
    }

