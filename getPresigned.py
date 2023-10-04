import json
import logging
import boto3
from botocore.exceptions import ClientError
import uuid
import re

BUCKET_NAME = "<YOUR-BUCKET-NAME>"
REGION_NAME = "<YOUR-REGION>"

def create_presigned_url(bucket_name, object_name, expiration=600):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', region_name=REGION_NAME, config=boto3.session.Config(signature_version='s3v4'))
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return "Error", None
    except Exception as e:
        logging.error(e)
        return "Error", None

    # The response contains the presigned URL
    return response, object_name

def lambda_handler(event, context):
    params = event['queryStringParameters']

    base_file_name = re.sub(r'[^\w\-.]', '-', params['fileName'])  # Sanitize the filename

    # Extract the extension from the sanitized filename
    extension = ".jpg"  # default to .jpg
    if '.' in base_file_name:
        extension = base_file_name.rsplit('.', 1)[-1]
        if not re.match(r'^\.\w+$', extension):
            extension = ".jpg"  # if extension is not valid, default to .jpg

    object_key = f"input/{base_file_name}"

    s3_client = boto3.client('s3', region_name=REGION_NAME)
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=object_key)
        # If no exception, the object exists, so add UUID to the file name
        base_file_name = f"{uuid.uuid4()}_{base_file_name}"
        object_key = f"input/{base_file_name}{extension}"
    except ClientError as e:
        if e.response['Error']['Code'] != '404':
            logging.error(e)
            return {
                'statusCode': 500,
                'body': json.dumps({'message': 'Internal server error'})
            }
        object_key += extension  # Append the extension if the file doesn't already exist

    presigned_url, final_object_name = create_presigned_url(BUCKET_NAME, object_key)
    

    
    if presigned_url == "Error":
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error'})
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
        'body': json.dumps({
            'presigned_url': presigned_url,
            'fileName': final_object_name.split('/')[-1]
        })
    }
