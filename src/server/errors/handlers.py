from fastapi import status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from pydantic import ValidationError


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
        content=jsonable_encoder({"detail": str(exc)}),
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

exception_handlers = {
    Exception: exception_handler,
    ValidationError: validation_exception_handler,
}
