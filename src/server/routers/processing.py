import json
from uuid import uuid4

from botocore.client import BaseClient
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import StreamingResponse

from src.server.config import Settings
from src.server.dependencies.config import get_settings
from src.server.dependencies.s3 import get_s3_client
from src.server.utils.annihilator import SpleeterSeparator

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
    file_content = await file.read()
    separator = SpleeterSeparator(
        s3_client=s3,
        s3_bucket=settings.S3_BUCKET,
    )
    separator._log(f"Processing audio... {file.filename}")

    async def event_generator():
        try:
            for data in separator.separate_with_progress(
                audio_bytes=file_content,
                filename=str(uuid4()),
                s3_output_prefix="processed/",
            ):
                yield f"data: {json.dumps(data)}\n\n"
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        finally:
            yield "event: close\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
