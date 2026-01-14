from helpers import functions

def validate(files):
    if len(files) < 1:
        return {
            'status': 'error',
            'message': 'Files need to be uploaded'
        }

    files_to_process = []

    for file in files:
        if functions.allowed_file(file.filename):
            files_to_process.append(file)

    if len(files_to_process) == 0:
        return {
            'status': 'error',
            'message': 'All files format not accepted',
        }

    return {
        'status': 'success',
        'files': files_to_process
    }