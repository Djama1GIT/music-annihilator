import logging
from typing import Callable, Generator

from botocore.client import BaseClient  # type: ignore[import-untyped]
from fastapi import Depends

from src.server.core.config import Settings
from src.server.services.s3.client import S3Client

logger = logging.getLogger(__name__)

# Global S3 client instance with lazy initialization
_s3_client = S3Client(logger=logger)


def get_s3_client(get_settings) -> Callable[[Settings], Generator[BaseClient, None, None]]:
    """
    Factory function to create a dependency for obtaining an S3 client.

    This function returns a dependency that provides a configured and authenticated
    S3 client instance. The client is initialized lazily and maintains a single
    global instance with automatic reconnection capabilities.

    Parameters:
        get_settings: Dependency function to retrieve application settings.

    Returns:
        A FastAPI dependency function that yields a configured S3 client.
    """

    def _get_s3_client(settings: Settings = Depends(get_settings)) -> Generator[BaseClient, None, None]:
        """
        Inner dependency function that manages the S3 client lifecycle.

        Parameters:
            settings (Settings): Application settings containing S3 configuration.

        Returns:
            BaseClient: Authenticated and configured boto3 S3 client.

        Raises:
            RuntimeError: If S3 client initialization fails.
        """
        global _s3_client

        if not _s3_client.is_initialized:
            _s3_client.initialize(settings)
        else:
            _s3_client.reconnect_if_needed()

        yield from _s3_client.get_client()

    return _get_s3_client
