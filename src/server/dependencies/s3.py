from botocore.client import BaseClient
from fastapi import Depends

from src.server.config import Settings
from src.server.services.boto import S3Client

_s3_client = S3Client()


def get_s3_client(get_settings):
    def _get_s3_client(settings: Settings = Depends(get_settings)) -> BaseClient:
        global _s3_client

        if not _s3_client.is_initialized:
            _s3_client.initialize(settings)
        else:
            _s3_client.reconnect_if_needed()

        return _s3_client.get_client()

    return _get_s3_client
