from fastapi import status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from pydantic import ValidationError

from src.server.errors import CustomError
from src.server.errors.s3 import S3FileNotFound


# noinspection PyUnusedLocal
async def exception_handler(
        request: Request,
        exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for all uncaught exceptions.

    Parameters:
        request: The incoming request (unused)
        exc: The exception that was raised

    Returns:
        JSONResponse: 500 error response with exception details
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": "Internal Server Error"}),
    )


# noinspection PyUnusedLocal
async def validation_exception_handler(
        request: Request,
        exc: ValidationError,
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.

    Parameters:
        request: The incoming request (unused)
        exc: The validation error that occurred

    Returns:
        JSONResponse: 422 error response with validation error details
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


# noinspection PyUnusedLocal
async def custom_error_handler(
        request: Request,
        exc: CustomError,
) -> JSONResponse:
    """
    Handler for Custom validation errors.

    Parameters:
        request: The incoming request (unused)
        exc: The validation error that occurred

    Returns:
        JSONResponse: 500 error response with custom error details
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({"detail": str(exc)}),
    )


# noinspection PyUnusedLocal
async def file_not_found_handler(
        request: Request,
        exc: S3FileNotFound,
) -> JSONResponse:
    """
    Handler for S3 file not found errors.

    Parameters:
        request: The incoming request (unused)
        exc: The validation error that occurred

    Returns:
        JSONResponse: 404 error response with file not found details
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": str(exc)}),
    )

exception_handlers = {
    Exception: exception_handler,
    ValidationError: validation_exception_handler,
    CustomError: custom_error_handler,
    S3FileNotFound: file_not_found_handler,
}
