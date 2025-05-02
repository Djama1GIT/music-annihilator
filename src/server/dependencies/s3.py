import boto3
from botocore.client import BaseClient
from fastapi import Depends

from src.server.config import Settings


def get_s3_client(get_settings):
    def _get_s3_client(settings: Settings = Depends(get_settings)) -> BaseClient:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )

        existing_buckets = [bucket['Name'] for bucket in s3.list_buckets()['Buckets']]

        if settings.S3_BUCKET not in existing_buckets:
            s3.create_bucket(Bucket=settings.S3_BUCKET)

        return s3

    return _get_s3_client
