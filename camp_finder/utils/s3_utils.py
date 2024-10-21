import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')

BUCKET_NAME = "daxman-campsite-finder"

def download_s3_file(S3_KEY, LOCAL_FILE):
    # Download the file from S3
    if os.path.exists(LOCAL_FILE):
        os.remove(LOCAL_FILE)
    try:
        print(f"Downloading {S3_KEY} from bucket {BUCKET_NAME} to {LOCAL_FILE}...")
        s3.download_file(BUCKET_NAME, S3_KEY, LOCAL_FILE)
        print(f"File downloaded successfully to {LOCAL_FILE}")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")






