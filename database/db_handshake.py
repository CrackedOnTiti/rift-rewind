import boto3
from dotenv import load_dotenv
import os

load_dotenv()

def get_dynamodb_reasources():
    region = os.getenv('AWS_DEFAULT_REGION')
 
    if not region:
        raise ValueError(
            "AWS_DEFAULT_REGION not found in environment variables! "
            "Make sure .env file exists and contains the correct reigon"
        )
    return boto3.resource('dynamodb', region_name=region)

s3 = boto3.resource('s3')

for bucket in s3.buckets.all():
    print(bucket.name)

# s3.upload_file('local.txt', 'mon-bucket', 'dossier/remote.txt')
# s3.download_file('mon-bucket', 'dossier/remote.txt', 'local_copy.txt')
