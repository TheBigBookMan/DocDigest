from flask import Flask, render_template, request
import helpers.functions

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

    if 'file' not in request.files:
        return {
            'status': 'error',
            'message': 'Files need to be uploaded'
        }

    # requested_file = request.files['file']
    print(request)

