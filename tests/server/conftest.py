from pathlib import Path
from unittest.mock import Mock, AsyncMock

import pytest
from fastapi import UploadFile

from src.server.annihilator.progress_tracker import ProgressTracker
from src.server.annihilator.spleeter import Spleeter
from src.server.annihilator.spleeter_sse import SpleeterSSE
from src.server.schemas.annihilator_sse import ProgressSSESchema


@pytest.fixture(autouse=True)
def setup_logging():
    """Configuring logging for tests"""
    import logging
    logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def mock_s3_client():
    return Mock()


@pytest.fixture
def spleeter_instance(mock_s3_client):
    return Spleeter(
        s3_client=mock_s3_client,
        s3_bucket="test-bucket",
        model="2stems",
        codec="mp3",
        bitrate="192k",
        enable_logging=True
    )


@pytest.fixture
def audio_data():
    with open(Path(__file__).parent / "test.mp3", "rb") as f:
        return f.read()


@pytest.fixture
def filename():
    return "test.mp3"


@pytest.fixture
def mock_progress_tracker():
    tracker = Mock(spec=ProgressTracker)
    tracker.update_progress = Mock(return_value=Mock(spec=ProgressSSESchema))
    tracker.error_update = Mock(return_value=Mock(spec=ProgressSSESchema))
    tracker.result_update = Mock(return_value=Mock(spec=ProgressSSESchema))
    return tracker


@pytest.fixture
def mock_settings():
    """Settings Mock"""
    settings = Mock()
    settings.S3_BUCKET = "test-bucket"
    return settings


@pytest.fixture
def mock_upload_file():
    """Downloadable file Mock"""
    file = Mock(spec=UploadFile)
    file.filename = "test_audio.mp3"
    file.read = AsyncMock(return_value=b"test audio content")
    return file


@pytest.fixture
def mock_spleeter_sse():
    """Mock SpleeterSSE"""
    return Mock(spec=SpleeterSSE)


@pytest.fixture
def mock_s3_response():
    """Мок ответа от S3"""
    response = {
        "Body": Mock(),
        "ContentType": "audio/mpeg",
        "ContentLength": 1024
    }
    return response
