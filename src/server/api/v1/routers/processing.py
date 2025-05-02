import json
from uuid import uuid4

from botocore.client import BaseClient
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from src.server.config import Settings
from src.server.dependencies.config import get_settings
from src.server.dependencies.s3 import get_s3_client
from src.server.annihilator.annihilator import SpleeterSeparator
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
    """Process audio file with Spleeter using Server-Sent Events for progress updates"""
    logger.info(f"Starting audio processing for file: {file.filename}")
    logger.debug(f"Initializing SpleeterSeparator")

    try:
        file_content = await file.read()
        logger.debug(f"Read file content, size: {len(file_content)} bytes")

        separator = SpleeterSeparator(
            s3_client=s3,
            s3_bucket=settings.S3_BUCKET,
        )
        logger.info(f"Processing audio... {file.filename}")

        unique_filename = str(uuid4())
        logger.info(f"Generated unique filename: {unique_filename}")

        async def event_generator():
            try:
                logger.debug("Starting SSE event generator")
                for data in separator.separate_with_progress(
                    audio_bytes=file_content,
                    filename=unique_filename,
                    s3_output_prefix="processed/",
                ):
                    logger.debug(f"Yielding progress update: {data}")
                    yield f"data: {json.dumps(data)}\n\n"

                logger.info("Audio processing completed successfully")
            except Exception as exc:
                logger.error(f"Error during audio processing: {str(exc)}", exc_info=True)
                yield f'data: {{"error": "{str(exc)}"}}\n\n'
            finally:
                logger.debug("Closing SSE stream")
                yield "event: close\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )

    except Exception as e:
        logger.error(
            f"Initial processing error for file {file.filename}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))
