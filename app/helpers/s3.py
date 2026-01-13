import boto3

s3 = boto3.client('s3')

def upload_file_to_s3(file_path, bucket, key):
    try:
        s3.upload_fileobj(file_path, bucket, key)
        return True

    except Exception as e:
        return f"Could not upload: {file_path}. Error: {e.message}"
