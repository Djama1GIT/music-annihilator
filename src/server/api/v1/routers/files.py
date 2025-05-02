from botocore.client import BaseClient
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from src.server.config import Settings
from src.server.dependencies.config import get_settings
from src.server.dependencies.s3 import get_s3_client

from src.server.logger import logger

router = APIRouter(
    prefix="/files",
    tags=["files"],
)


@router.get("/download-processed-file/")
async def download_processed_file(
        processed_filename: str = Query(alias="processed-filename"),
        result_filename: str = Query(alias="result-filename"),
        s3: BaseClient = Depends(get_s3_client(get_settings)),
        settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    """Download file from S3"""
    try:
        s3_key = f"processed/{processed_filename}/{result_filename}"

        logger.debug(f"Constructed S3 key: {s3_key}")

        response = s3.get_object(Bucket=settings.S3_BUCKET, Key=s3_key)
        logger.info("File successfully retrieved from S3")

        return StreamingResponse(
            response["Body"],
            media_type=response["ContentType"],
            headers={
                "Content-Disposition": f"attachment; filename={s3_key.split('/')[-1]}",
                "Content-Length": str(response["ContentLength"]),
            }
        )
    except s3.exceptions.NoSuchKey:
        logger.error(f"File not found in S3: {processed_filename}/{result_filename}")
        raise HTTPException(status_code=404, detail="File not found in S3")
    except Exception as e:
        logger.error(f"Error downloading file {processed_filename}/{result_filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
