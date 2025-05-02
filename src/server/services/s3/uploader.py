from pathlib import Path
from typing import Dict

from botocore.client import BaseClient
from botocore.exceptions import ClientError


class S3Uploader:
    def __init__(self, s3_client: BaseClient, s3_bucket: str, logger=None):
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket
        self.logger = logger

    def _log(self, message: str, level: str = "info"):
        if self.logger:
            getattr(self.logger, level)(f"{__class__.__name__}: {message}")

    def upload_file(self, file_path: Path, s3_key: str) -> bool:
        """Upload a file to S3 and return success status."""
        self._log(f"Attempting to upload file to S3: {file_path} -> {s3_key}")
        try:
            self.s3_client.upload_file(str(file_path), self.s3_bucket, s3_key)
            self._log(f"Successfully uploaded file to S3: {s3_key}")
            return True

        except ClientError as e:
            self._log(f"S3 upload error for {file_path}: {str(e)}", "error")
            return False

        except Exception as e:
            self._log(f"Unexpected error during S3 upload: {str(e)}", "error")
            return False

    def upload_files(self, files: Dict[str, Path], s3_prefix: str) -> bool:
        """Upload multiple files to S3 with a common prefix."""
        for stem, file_path in files.items():
            s3_key = f"{s3_prefix}/{stem}"
            if not self.upload_file(file_path, s3_key):
                return False

        return True
