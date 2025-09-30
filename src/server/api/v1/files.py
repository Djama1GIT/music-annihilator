from botocore.client import BaseClient  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from src.server.config import Settings
from src.server.dependencies.s3 import get_s3_client
from src.server.dependencies.settings import get_settings
from src.server.logger import logger

router = APIRouter(
    prefix="/files",
    tags=["files"],
)


@router.get("/download-processed-file/", summary="Download a processed file from S3 bucket.")
async def download_processed_file(
    processed_filename: str = Query(alias="processed-filename", min_length=1, description="The original filename"),
    result_filename: str = Query(alias="result-filename", min_length=1, description="The result filename"),
    s3: BaseClient = Depends(get_s3_client(get_settings)),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """
    Download a processed file from S3 bucket.

    This endpoint streams a file from S3 storage that was previously processed.
    The file is located in the 'processed/' prefix followed by the processed filename directory.

    Parameters:
        processed_filename (str): The name of the processing job/directory (from query parameter 'processed-filename').
        result_filename (str): The name of the result file to download (from query parameter 'result-filename').
        s3 (BaseClient): Authenticated S3 client (injected dependency).
        settings (Settings): Application settings (injected dependency).

    Returns:
        StreamingResponse: A streaming response containing the file data with appropriate headers.

    Raises:
        HTTPException: 404 if file not found in S3.
        HTTPException: 500 for any other errors.
    """
    s3_key = f"processed/{processed_filename}/{result_filename}"

    logger.debug(f"Constructed S3 key: {s3_key}")

    response = s3.get_object(Bucket=settings.S3_BUCKET, Key=s3_key)
    logger.info("File successfully retrieved from S3")

    return StreamingResponse(
        response["Body"],
        media_type=response["ContentType"],
        headers={
            "Content-Disposition":
                f"attachment; "
                f"filename={processed_filename}.{result_filename.split('.')[-1]}",
            "Content-Length": str(response["ContentLength"]),
        },
    )
