from fastapi import APIRouter

from src.server.api.v1.files import router as files_router_v1
from src.server.api.v1.processing import router as processing_router_v1

v1_router = APIRouter()

v1_router.include_router(processing_router_v1)
v1_router.include_router(files_router_v1)
