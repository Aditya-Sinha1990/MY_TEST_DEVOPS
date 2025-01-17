import boto3
import os
import zipfile
from datetime import datetime

# AWS Configuration (Environment Variables)
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
LOG_DIRECTORY = "/var/log"  # Adjust this path to where SSH logs are stored
ZIP_FILE_NAME = "ssh_logs.zip"

def zip_logs():
    """Compress SSH log files into a zip archive."""
    log_files = [f for f in os.listdir(LOG_DIRECTORY) if "auth.log" in f or "secure" in f]
    if not log_files:
        print("No SSH log files found.")
        return None
    
    with zipfile.ZipFile(ZIP_FILE_NAME, 'w') as zipf:
        for log_file in log_files:
            log_path = os.path.join(LOG_DIRECTORY, log_file)
            zipf.write(log_path, os.path.basename(log_path))
    print(f"Logs zipped into {ZIP_FILE_NAME}")
    return ZIP_FILE_NAME

def upload_to_s3(zip_file):
    """Upload the zip archive to S3."""
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
    )
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        s3_key = f"ssh_logs/{timestamp}_{zip_file}"
        s3.upload_file(zip_file, S3_BUCKET_NAME, s3_key)
        print(f"Uploaded {zip_file} to S3 bucket {S3_BUCKET_NAME} as {s3_key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

def main():
    zip_file = zip_logs()
    if zip_file:
        upload_to_s3(zip_file)
        os.remove(zip_file)

if __name__ == "__main__":
    main()
