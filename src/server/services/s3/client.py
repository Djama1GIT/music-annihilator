from logging import Logger
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, EndpointConnectionError

from src.server.config import Settings
from src.server.logger import logger


class S3Client:
    def __init__(self, _logger: Logger = logger):
        self._client: Optional[BaseClient] = None
        self._settings: Optional[Settings] = None
        self._logger = _logger
        self._logger.debug("S3Client initialized with no settings and no client")

    @property
    def is_initialized(self) -> bool:
        initialized = self._client is not None
        self._logger.debug(f"Checking if client is initialized: {initialized}")
        return initialized

    def initialize(self, settings: Settings) -> None:
        """Initializing the S3 client with the specified settings"""
        self._logger.info(
            f"Initializing S3 client with settings: endpoint={settings.S3_ENDPOINT_URL}, "
            f"region={settings.S3_REGION}, bucket={settings.S3_BUCKET}"
        )

        self._settings = settings
        self._reinitialize_client()

        self._ensure_bucket_exists()
        self._logger.info("S3 client initialized successfully")

    def _reinitialize_client(self) -> None:
        """Creating a new S3 client with current settings"""
        if self._settings is None:
            error_msg = "Settings must be initialized before creating client"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        self._logger.debug(
            f"Creating new S3 client with endpoint: {self._settings.S3_ENDPOINT_URL}"
        )
        try:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._settings.S3_ENDPOINT_URL,
                aws_access_key_id=self._settings.S3_ACCESS_KEY,
                aws_secret_access_key=self._settings.S3_SECRET_KEY,
                region_name=self._settings.S3_REGION,
            )
            self._logger.info("S3 client created successfully")
        except Exception as e:
            self._logger.error(f"Failed to create S3 client: {str(e)}")
            raise

    def _ensure_bucket_exists(self) -> None:
        """Checks the existence of a bucket and creates it if necessary"""
        if self._client is None or self._settings is None:
            error_msg = "Client and settings must be initialized"
            self._logger.error(error_msg)
            raise ValueError(error_msg)

        bucket_name = self._settings.S3_BUCKET
        self._logger.info(f"Checking bucket existence: {bucket_name}")

        try:
            existing_buckets = [
                bucket["Name"] for bucket in self._client.list_buckets()["Buckets"]
            ]
            self._logger.debug(f"Existing buckets: {existing_buckets}")

            if bucket_name not in existing_buckets:
                self._logger.info(f"Bucket {bucket_name} not found, creating new one")
                self._client.create_bucket(Bucket=bucket_name)
                self._logger.info(f"Bucket {bucket_name} created successfully")
            else:
                self._logger.debug(f"Bucket {bucket_name} already exists")
        except (ClientError, EndpointConnectionError) as e:
            self._logger.error(f"Error checking/creating bucket {bucket_name}: {str(e)}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error during bucket verification: {str(e)}")
            raise

    def get_client(self) -> BaseClient:
        """Returns the S3 client, restoring the connection if necessary"""
        if self._client is None:
            if self._settings is None:
                error_msg = "S3 client not initialized"
                self._logger.error(error_msg)
                raise ValueError(error_msg)

            self._logger.info("Client is None, reinitializing...")
            self._reinitialize_client()

        return self._client

    def check_connection(self) -> bool:
        """Checks the connection with S3"""
        self._logger.debug("Checking S3 connection")
        try:
            self._client.list_buckets()
            self._logger.debug("S3 connection check successful")
            return True
        except (ClientError, EndpointConnectionError) as e:
            self._logger.warning(f"S3 connection check failed: {str(e)}")
            return False
        except Exception as e:
            self._logger.error(f"Unexpected error during connection check: {str(e)}")
            return False

    def reconnect_if_needed(self) -> bool:
        """Reconnects if the connection is lost, returns True if there was a reconnection"""
        if not self.check_connection():
            self._logger.warning("S3 connection lost, attempting to reconnect...")
            try:
                self._reinitialize_client()
                self._logger.info("Reconnection attempt completed")
                return True
            except Exception as e:
                self._logger.error(f"Failed to reconnect: {str(e)}")
                return False
        self._logger.debug("No reconnection needed")
        return False
