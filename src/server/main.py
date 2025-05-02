from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import ValidationError

from src.server.config import Settings
from src.server.api.v1.routers.processing import router as processing_router_v1
from src.server.api.v1.routers.files import router as files_router_v1

settings = Settings()

app = FastAPI(
    title=settings.TITLE,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    summary=settings.SUMMARY,
    contact=settings.CONTACT,
    license_info=settings.LICENSE_INFO,
)
v1 = FastAPI()

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

app.include_router(processing_router_v1, prefix="/api/latest")
app.include_router(files_router_v1, prefix="/api/latest")

v1.include_router(processing_router_v1)
v1.include_router(files_router_v1)

app.mount("/api/v1", v1)


# noinspection PyUnusedLocal
@app.exception_handler(Exception)
async def exception_error(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder({'detail': str(exc)})
    )


# noinspection PyUnusedLocal
@app.exception_handler(ValidationError)
async def validation_exception_error(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors()})
    )
