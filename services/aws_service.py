import boto3
import os
import pandas as pd
from dotenv import load_dotenv
from io import StringIO

COLUMNS = [
    'id',
    'web_id',
    'title',
    'link',
    'date_posted',
    'summary',
    'source',
    'text',
    'unique_id',
    'created_at',
    'updated_at',
    'is_relevant',
    'collision_location',
    'collision_date'
]


def upload_file_s3(df, file_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    buffer = StringIO()
    df.to_csv(buffer, index=False)

    # Upload the file
    load_dotenv()
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    bucket = os.getenv('S3_BUCKET')

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        s3_client.put_object(Bucket=bucket, Key=file_name, Body=buffer.getvalue())
    except Exception as e:
        print(e)
        return False
    return True


def read_file_s3(file_name):
    """Read transaction list from an S3 bucket

    :param file_name: File to read
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    load_dotenv()
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET')

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        df = pd.read_csv(response['Body'])
    except Exception as e:
        print(e)
        return pd.DataFrame(columns=COLUMNS)

    return df