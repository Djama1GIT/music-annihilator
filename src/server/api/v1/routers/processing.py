from uuid import uuid4

from botocore.client import BaseClient  # type: ignore[import-untyped]
from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from src.server.annihilator.spleeter_sse import SpleeterSSE
from src.server.config import Settings
from src.server.dependencies.settings import get_settings
from src.server.dependencies.s3 import get_s3_client
from src.server.logger import logger

router = APIRouter(
    prefix="/processing",
    tags=["Processing"],
)


@router.post("/spleeter-sse")
async def process_with_sse(
    file: UploadFile = File(...),
    s3: BaseClient = Depends(get_s3_client(get_settings)),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    Process audio file with Spleeter separation using Server-Sent Events (SSE) for real-time progress updates.

    This endpoint accepts an audio file, processes it using Spleeter,
    and returns a Server-Sent Events stream with progress updates and final results.
    The processed files are stored in S3 bucket with a unique identifier.

    Parameters:
        file (UploadFile): Audio file to process (required, multipart/form-data).
        s3 (BaseClient): Authenticated S3 client (injected dependency).
        settings (Settings): Application configuration (injected dependency).

    Returns:
        StreamingResponse: SSE stream with events containing:
        - Progress updates during processing
        - Success/failure status
        - UUID of the processed audio files

    Raises:
        HTTPException: 500 if any error occurs during processing

    Notes:
        - Uses Spleeter for audio source separation
        - Generates unique UUID for each processing job
        - Stores results in configured S3 bucket
        - Stream format follows Server-Sent Events specification
    """
    logger.info(f"Starting audio processing for file: {file.filename}")
    logger.debug(f"Initializing SpleeterSeparator")

    try:
        file_content = await file.read()
        logger.debug(f"Read file content, size: {len(file_content)} bytes")

        annihilator = SpleeterSSE(
            s3_client=s3,
            s3_bucket=settings.S3_BUCKET,
        )
        logger.info(f"Processing audio... {file.filename}")

        unique_filename = str(uuid4())
        logger.info(f"Generated unique filename: {unique_filename}")

        return StreamingResponse(
            annihilator.sse_generator(audio_bytes=file_content, filename=unique_filename),
            media_type="text/event-stream",
        )

    except Exception as e:
        logger.error(
            f"Initial processing error for file {file.filename}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
