from logging import Logger
from typing import Optional

from src.server.enums.logger import LoggerLevelsEnum
from src.server.enums.progress import AnnihilationProgressEnum
from src.server.schemas.annihilator_sse import ResultSSESchema, ErrorSSESchema, ProgressSSESchema


class ProgressTracker:
    """
    A class to track and log operation progress and generate SSE schemas for client communication.

    This class provides methods to update progress, report results, and handle errors while
    maintaining consistent logging and SSE event generation.

    Parameters:
        logger (Logger): Optional logger instance for tracking progress and errors.
    """

    def __init__(self, logger: Logger = None) -> None:
        """
        Initialize the ProgressTracker with an optional logger.

        Parameters:
            logger (Logger, optional): Python logger instance for progress tracking.
                                      Defaults to None (no logging).
        """
        self.logger = logger

    def _log(self, message: str, *, level: LoggerLevelsEnum = LoggerLevelsEnum.INFO, exc_info=False):
        """
        Internal method for consistent logging with class name prefix.

        Parameters:
            message (str): The message to log.
            level (LoggerLevelsEnum, optional): Logging level. Defaults to INFO.
        """
        if self.logger:
            getattr(self.logger, level.value)(f"{self.__class__.__name__}: {message}", exc_info=exc_info)

    def update_progress(self, progress: AnnihilationProgressEnum, message: Optional[str] = "") -> ProgressSSESchema:
        """
        Generate a progress update event with logging.

        Parameters:
            progress (AnnihilationProgressEnum): The current progress state/enum value.
            message (str, optional): Additional progress details. Defaults to empty string.

        Returns:
            ProgressSSESchema: SSE-compatible progress update schema.
        """
        self._log(f"Progress: {progress}% - {message}")
        return ProgressSSESchema(progress=progress, message=message)

    def result_update(self, result: str, message: Optional[str] = "") -> ResultSSESchema:
        """
        Generate a result event with logging.

        Parameters:
            result (str): The actual result data.
            message (str): Message or details related to the result.

        Returns:
            ResultSSESchema: SSE-compatible result schema.
        """
        self._log(f"Result progress: {message}")
        return ResultSSESchema(result=result, message=message)

    def error_update(self, error: str) -> ErrorSSESchema:
        """
        Generate an error event with error-level logging.

        Parameters:
            error (str): Error description or message.

        Returns:
            ErrorSSESchema: SSE-compatible error schema.
        """
        self._log(f"Error: {error}", level=LoggerLevelsEnum.ERROR)
        return ErrorSSESchema(error=error)
