from logging import Logger
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError, EndpointConnectionError

from src.server.config import Settings
from src.server.enums.logger import LoggerLevelsEnum


class S3Client:
    """
    A managed client for interacting with S3 storage service.

    Provides connection management, automatic reconnection, and bucket verification.
    Handles all S3 operations with proper error handling and logging.

    Parameters:
        logger (Logger, optional): Python logger instance for operation tracking.
                                  Defaults to None.

    Attributes:
        _client (Optional[BaseClient]): Internal boto3 S3 client instance
        _settings (Optional[Settings]): Configuration settings for S3 connection
        _logger (Logger): Logger instance for operation tracking
    """

    def __init__(self, logger: Logger = None):
        """Initialize the S3 client manager in unconfigured state."""
        self._client: Optional[BaseClient] = None
        self._settings: Optional[Settings] = None
        self._logger = logger
        self._log(
            message="S3Client initialized with no settings and no client",
            level=LoggerLevelsEnum.DEBUG,
        )

    def _log(
        self,
        message: str,
        *,
        level: LoggerLevelsEnum = LoggerLevelsEnum.INFO,
        exc_info=False,
    ):
        """
        Internal logging helper with standardized formatting.

        Parameters:
            message (str): Log message content
            level (LoggerLevelsEnum): Log severity level. Defaults to INFO.
            exc_info (bool): Whether to include exception info. Defaults to False.
        """
        if self._logger:
            getattr(self._logger, level.value)(
                f"{self.__class__.__name__}: {message}",
                exc_info=exc_info,
            )

    @property
    def is_initialized(self) -> bool:
        """
        Check if the client has been properly initialized.

        Returns:
            bool: True if client is ready for use, False otherwise
        """
        initialized = self._client is not None
        self._log(
            f"Checking if client is initialized: {initialized}",
            level=LoggerLevelsEnum.DEBUG,
        )
        return initialized

    def initialize(self, settings: Settings) -> None:
        """
        Configure and initialize the S3 client with application settings.

        Parameters:
            settings (Settings): Application configuration containing S3 credentials

        Raises:
            RuntimeError: If client creation fails
            ValueError: If settings are invalid
        """
        self._log(
            f"Initializing S3 client with settings: endpoint={settings.S3_ENDPOINT_URL}, "
            f"region={settings.S3_REGION}, bucket={settings.S3_BUCKET}"
        )

        self._settings = settings
        self._reinitialize_client()

        self._ensure_bucket_exists()
        self._log("S3 client initialized successfully")

    def _reinitialize_client(self) -> None:
        """
        Create new S3 client instance with current settings.

        Raises:
            ValueError: If settings are not configured
            RuntimeError: If client creation fails
        """
        if self._settings is None:
            error_msg = "Settings must be initialized before creating client"
            self._log(error_msg, level=LoggerLevelsEnum.ERROR)
            raise ValueError(error_msg)

        self._log(
            f"Creating new S3 client with endpoint: {self._settings.S3_ENDPOINT_URL}",
            level=LoggerLevelsEnum.DEBUG,
        )
        try:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._settings.S3_ENDPOINT_URL,
                aws_access_key_id=self._settings.S3_ACCESS_KEY,
                aws_secret_access_key=self._settings.S3_SECRET_KEY,
                region_name=self._settings.S3_REGION,
            )
            self._log("S3 client created successfully")
        except Exception as e:
            self._log(
                message=f"Failed to create S3 client: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
            )
            raise RuntimeError(f"Failed to create S3 client: {str(e)}")

    def _ensure_bucket_exists(self) -> None:
        """
        Verify and create bucket if it doesn't exist.

        Raises:
            ValueError: If client or settings are not initialized
            RuntimeError: If bucket operation fails
        """
        if self._client is None or self._settings is None:
            error_msg = "Client and settings must be initialized"
            self._log(error_msg, level=LoggerLevelsEnum.ERROR)
            raise ValueError(error_msg)

        bucket_name = self._settings.S3_BUCKET
        self._log(f"Checking bucket existence: {bucket_name}")

        try:
            existing_buckets = [
                bucket["Name"] for bucket in self._client.list_buckets()["Buckets"]
            ]
            self._log(
                message=f"Existing buckets: {existing_buckets}",
                level=LoggerLevelsEnum.DEBUG,
            )

            if bucket_name not in existing_buckets:
                self._log(f"Bucket {bucket_name} not found, creating new one")
                self._client.create_bucket(Bucket=bucket_name)
                self._log(f"Bucket {bucket_name} created successfully")
            else:
                self._log(
                    message=f"Bucket {bucket_name} already exists",
                    level=LoggerLevelsEnum.DEBUG,
                )
        except (ClientError, EndpointConnectionError) as e:
            self._log(
                message=f"Error checking/creating bucket {bucket_name}: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
            )
            raise RuntimeError(
                f"Error checking/creating bucket {bucket_name}: {str(e)}"
            )
        except Exception as e:
            self._log(
                message=f"Unexpected error during bucket verification: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
            )
            raise RuntimeError(f"Unexpected error during bucket verification: {str(e)}")

    def get_client(self) -> BaseClient:
        """
        Get the configured S3 client, ensuring it's ready for use.

        Returns:
            BaseClient: Configured and ready S3 client instance

        Raises:
            ValueError: If client is not initialized
        """
        if self._client is None:
            if self._settings is None:
                error_msg = "S3 client not initialized"
                self._log(error_msg, level=LoggerLevelsEnum.ERROR)
                raise ValueError(error_msg)

            self._log("Client is None, reinitializing...")
            self._reinitialize_client()

        return self._client

    def check_connection(self) -> bool:
        """
        Verify active connection to S3 service.

        Returns:
            bool: True if connection is active, False otherwise
        """
        self._log(
            message="Checking S3 connection",
            level=LoggerLevelsEnum.DEBUG,
        )
        try:
            self._client.list_buckets()
            self._log(
                message="S3 connection check successful",
                level=LoggerLevelsEnum.DEBUG,
            )
            return True
        except (ClientError, EndpointConnectionError) as e:
            self._log(
                message=f"S3 connection check failed: {str(e)}",
                level=LoggerLevelsEnum.WARNING,
            )
            return False
        except Exception as e:
            self._log(
                f"Unexpected error during connection check: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
            )
            return False

    def reconnect_if_needed(self) -> bool:
        """
        Reconnect to S3 if connection is lost.

        Returns:
            bool: True if reconnection was performed, False otherwise
        """
        if not self.check_connection():
            self._log(
                message="S3 connection lost, attempting to reconnect...",
                level=LoggerLevelsEnum.WARNING,
            )
            try:
                self._reinitialize_client()
                self._log("Reconnection attempt completed")
                return True
            except Exception as e:
                self._log(
                    message=f"Failed to reconnect: {str(e)}",
                    level=LoggerLevelsEnum.ERROR,
                )
                return False
        self._log(
            message="No reconnection needed",
            level=LoggerLevelsEnum.DEBUG,
        )
        return False
