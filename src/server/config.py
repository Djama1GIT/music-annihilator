import json
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    APP_FILES_PATH: Path

    TITLE: str
    DESCRIPTION: str
    SUMMARY: str
    VERSION: str
    CONTACT: Dict[str, str]
    LICENSE_INFO: Dict[str, str]

    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str
    S3_BUCKET: str

    @field_validator('CONTACT', 'LICENSE_INFO', 'ALLOW_ORIGINS', 'ALLOW_METHODS', 'ALLOW_HEADERS', mode='before')
    def parse_json(cls, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value
