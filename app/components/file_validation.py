from helpers import functions

def validate(files):
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
        }

    return {
        'status': 'success',
        'files': files_to_process
    }