from typing import Optional

from pydantic import BaseModel

from src.server.enums.progress import AnnihilationProgressEnum


class ProgressSSESchema(BaseModel):
    """
    Base Server-Sent Event (SSE) schema for progress updates.

    Attributes:
        progress (AnnihilationProgressEnum): Current progress state enum value
        message (Optional[str]): Optional human-readable progress message.
    """

    progress: AnnihilationProgressEnum
    message: Optional[str] = None


class ErrorSSESchema(ProgressSSESchema):
    """
    SSE schema for error events during annihilation process.

    Extends the base progress schema with error-specific fields.
    Automatically sets progress state to ERROR.

    Attributes:
        progress (AnnihilationProgressEnum): Always set to ERROR state.
        error (str): Detailed error message.
        message (Optional[str]): Optional additional context message.
            Inherited from ProgressSSESchema.
    """

    progress: AnnihilationProgressEnum = AnnihilationProgressEnum.ERROR
    error: str


class ResultSSESchema(ProgressSSESchema):
    """
    SSE schema for final result events.

    Used to send the final successful result of an annihilation process.
    Automatically sets progress state to DONE.

    Attributes:
        progress (AnnihilationProgressEnum): Always set to DONE state.
        result (str): The final result data.
        message (Optional[str]): Optional completion message.
            Inherited from ProgressSSESchema.
    """
    progress: AnnihilationProgressEnum = AnnihilationProgressEnum.DONE
    result: str
