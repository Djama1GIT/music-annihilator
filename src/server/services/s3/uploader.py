from logging import Logger
from pathlib import Path
from typing import Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError

from src.server.enums.logger import LoggerLevelsEnum


class S3Uploader:
    """
    A utility class for uploading files to S3 storage.

    Provides methods for single and batch file uploads with consistent logging
    and error handling.

    Parameters:
        s3_client (BaseClient): Initialized boto3 S3 client
        s3_bucket (str): Target S3 bucket name
        logger (Logger, optional): Python logger instance for operation tracking

    Attributes:
        s3_client (BaseClient): Configured S3 client instance
        s3_bucket (str): Destination bucket name
        logger (Logger): Optional logger for operation tracking
    """

    def __init__(self, s3_client: BaseClient, s3_bucket: str, logger: Logger = None):
        """Initialize the S3 uploader with client, bucket and optional logger."""
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket
        self.logger = logger

    def _log(
        self,
        message: str,
        *,
        level: LoggerLevelsEnum = LoggerLevelsEnum.INFO,
        exc_info: bool = False,
    ):
        """
        Internal logging helper with class name prefix and customizable level.

        Parameters:
            message (str): Log message content
            level (LoggerLevelsEnum, optional): Log severity level. Defaults to INFO.
            exc_info (bool, optional): Whether to include exception info. Defaults to False.
        """
        if self.logger:
            getattr(self.logger, level.value)(
                f"{self.__class__.__name__}: {message}",
                exc_info=exc_info,
            )

    def upload_file(self, file_path: Path, s3_key: str) -> bool:
        """
        Upload a single file to S3 storage.

        Parameters:
            file_path (Path): Local filesystem path to the source file
            s3_key (str): Destination key/path in S3 bucket

        Returns:
            bool: True if upload succeeded, False if any error occurred

        Raises:
            ClientError: For AWS-specific S3 operation failures
            Exception: For unexpected upload errors
        """
        self._log(f"Attempting to upload file to S3: {file_path} -> {s3_key}")
        try:
            self.s3_client.upload_file(str(file_path), self.s3_bucket, s3_key)
            self._log(f"Successfully uploaded file to S3: {s3_key}")
            return True

        except ClientError as e:
            self._log(
                message=f"S3 upload error for {file_path}: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
                exc_info=True,
            )
            return False

        except Exception as e:
            self._log(
                message=f"Unexpected error during S3 upload: {str(e)}",
                level=LoggerLevelsEnum.ERROR,
                exc_info=True,
            )
            return False

    def upload_files(self, files: Dict[str, Path], s3_prefix: str) -> bool:
        """
        Upload multiple files to S3 under a common prefix.

        Parameters:
            files (Dict[str, Path]): Mapping of filename stems to local file paths
            s3_prefix (str): Common prefix for all uploaded files in S3

        Returns:
            bool: True if all uploads succeeded, False if any failed

        Note:
            Stops on first failure and returns False immediately
        """
        for stem, file_path in files.items():
            s3_key = f"{s3_prefix}/{stem}"
            if not self.upload_file(file_path, s3_key):
                return False

        return True
