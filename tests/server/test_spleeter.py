from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from src.server.annihilator.progress_tracker import ProgressTracker
from src.server.annihilator.spleeter import Spleeter
from src.server.enums.logging import LoggingLevelsEnum
from src.server.errors.spleeter import SpleeterError
from src.server.schemas.annihilator_sse import ResultSSESchema, ErrorSSESchema
from src.server.services.s3.uploader import S3Uploader


def test_init(mock_s3_client):
    """Class initialization test"""
    spleeter = Spleeter(
        s3_client=mock_s3_client,
        s3_bucket="test-bucket",
        model="4stems",
        codec="wav",
        bitrate="320k",
        enable_logging=False
    )

    assert spleeter.model == "4stems"
    assert spleeter.codec == "wav"
    assert spleeter.bitrate == "320k"
    assert spleeter.logger is None
    assert isinstance(spleeter.s3_uploader, S3Uploader)
    assert isinstance(spleeter.progress_tracker, ProgressTracker)


def test_init_default_params(mock_s3_client):
    """Initialization test with default parameters"""
    spleeter = Spleeter(
        s3_client=mock_s3_client,
        s3_bucket="test-bucket"
    )

    assert spleeter.model == "2stems"
    assert spleeter.codec == "mp3"
    assert spleeter.bitrate == "192k"
    assert spleeter.logger is not None


def test_log_with_logger(spleeter_instance):
    """Logging test with the logger enabled"""
    with patch.object(spleeter_instance.logger, 'info') as mock_log:
        spleeter_instance._log("test message")
        mock_log.assert_called_once()


def test_log_without_logger(mock_s3_client):
    """Logging test with the logger disabled"""
    spleeter = Spleeter(
        s3_client=mock_s3_client,
        s3_bucket="test-bucket",
        enable_logging=False
    )

    # There should be no exception
    spleeter._log("test message")


def test_log_different_levels(spleeter_instance):
    """Logging test with different levels"""
    with patch.object(spleeter_instance.logger, 'error') as mock_error_log:
        spleeter_instance._log(
            "error message",
            level=LoggingLevelsEnum.ERROR,
            exc_info=True
        )
        mock_error_log.assert_called_once()


@pytest.mark.asyncio
async def test_run_spleeter_command_success(spleeter_instance):
    """Test of successful execution of the spleeter command"""
    input_path = Path("/tmp/test.mp3")
    output_dir = Path("/tmp/output")

    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        # We are cleaning the process with successful completion
        mock_process = AsyncMock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.pid = 1234
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        _out_check = False
        _err_check = False

        # Mocking reading streams
        async def mock_out_readline():
            nonlocal _out_check
            if not _out_check:
                _out_check = True
                return b"test output\n"

        async def mock_err_readline():
            nonlocal _err_check
            if not _err_check:
                _err_check = True
                return b"error output\n"

        mock_process.stdout.readline = mock_out_readline
        mock_process.stderr.readline = mock_err_readline

        mock_subprocess.return_value = mock_process

        return_code = await spleeter_instance._run_spleeter_command(input_path, output_dir)

        assert return_code == 0
        mock_subprocess.assert_called_once()


@pytest.mark.asyncio
async def test_run_spleeter_command_failure(spleeter_instance):
    """Test of unsuccessful execution of the spleeter command"""
    input_path = Path("/tmp/test.mp3")
    output_dir = Path("/tmp/output")

    with patch('asyncio.create_subprocess_exec') as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.wait = AsyncMock(return_value=1)
        mock_process.pid = 1234
        mock_process.stdout = AsyncMock()
        mock_process.stderr = AsyncMock()

        _out_check = False
        _err_check = False

        # Mocking reading streams
        async def mock_out_readline():
            nonlocal _out_check
            if not _out_check:
                _out_check = True
                return b"test output\n"

        async def mock_err_readline():
            nonlocal _err_check
            if not _err_check:
                _err_check = True
                return b"error output\n"

        mock_process.stdout.readline = mock_out_readline
        mock_process.stderr.readline = mock_err_readline

        mock_subprocess.return_value = mock_process

        return_code = await spleeter_instance._run_spleeter_command(input_path, output_dir)

        assert return_code == 1


@pytest.mark.asyncio
async def test_run_spleeter_command_exception(spleeter_instance):
    """Exception test when executing the spleeter command"""
    input_path = Path("/tmp/test.mp3")
    output_dir = Path("/tmp/output")

    with patch('asyncio.create_subprocess_exec', side_effect=Exception("Process error")):
        with pytest.raises(SpleeterError):
            await spleeter_instance._run_spleeter_command(input_path, output_dir)


def test_get_output_files(spleeter_instance, tmp_path):
    """Test for getting output files"""
    # Creating test files
    test_files = ["vocals.mp3", "accompaniments.mp3"]
    for file in test_files:
        (tmp_path / file).touch()

    result = spleeter_instance._get_output_files(tmp_path)

    assert len(result) == 2
    assert "vocals" in result
    assert "accompaniments" in result
    assert all(isinstance(path, Path) for path in result.values())


def test_get_output_files_empty(spleeter_instance, tmp_path):
    """Test of getting files from an empty directory"""
    result = spleeter_instance._get_output_files(tmp_path)
    assert result == {}


def test_get_output_files_nonexistent(spleeter_instance):
    """Test of getting files from a non-existent directory"""
    with pytest.raises(FileNotFoundError):
        spleeter_instance._get_output_files(Path("/nonexistent/path"))


@pytest.mark.asyncio
async def test_separate_with_progress_success(spleeter_instance, audio_data, filename):
    """Test of successful audio separation with event"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run, \
            patch.object(spleeter_instance, '_get_output_files') as mock_get_files, \
            patch.object(spleeter_instance.s3_uploader, 'upload_file') as mock_upload:

        # Setting up mocks
        mock_run.return_value = 0
        mock_get_files.return_value = {
            "vocals": Path("/tmp/vocals.mp3"),
            "accompaniments": Path("/tmp/accompaniments.mp3")
        }
        mock_upload.return_value = True

        # Collecting all yield values
        progress_events = []
        async for event in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename,
                s3_output_prefix="test/"
        ):
            progress_events.append(event)

        assert len(progress_events) >= 5  # STARTING_WORK, WORK_STARTED, WORK_COMPLETED, FINALIZING_WORK, RESULT
        result = any([isinstance(event, ResultSSESchema) for event in progress_events])
        assert result


@pytest.mark.asyncio
async def test_separate_with_progress_spleeter_failure(spleeter_instance, audio_data, filename):
    """Spleeter failure test"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run:
        mock_run.return_value = 1  # Non-zero exit code

        progress_events = []
        async for event in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename
        ):
            progress_events.append(event)

        # error_update should be called
        error = any([isinstance(event, ErrorSSESchema) for event in progress_events])
        assert error


@pytest.mark.asyncio
async def test_separate_with_progress_no_output_files(spleeter_instance, audio_data, filename):
    """Test the case when there are no output files"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run, \
            patch.object(spleeter_instance, '_get_output_files') as mock_get_files:

        mock_run.return_value = 0
        mock_get_files.return_value = {}  # No output files

        progress_events = []
        async for event in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename
        ):
            progress_events.append(event)

        # error_update should be called
        error = any([isinstance(event, ErrorSSESchema) for event in progress_events])
        assert error


@pytest.mark.asyncio
async def test_separate_with_progress_upload_failure(spleeter_instance, audio_data, filename):
    """Failed upload test in S3"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run, \
            patch.object(spleeter_instance, '_get_output_files') as mock_get_files, \
            patch.object(spleeter_instance.s3_uploader, 'upload_file') as mock_upload:

        mock_run.return_value = 0
        mock_get_files.return_value = {"vocals": Path("/tmp/vocals.mp3")}
        mock_upload.return_value = False  # Upload failed

        progress_events = []
        async for event in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename
        ):
            progress_events.append(event)

        # error_update should be called
        error = any([isinstance(event, ErrorSSESchema) for event in progress_events])
        assert error


@pytest.mark.asyncio
async def test_separate_with_progress_exception(spleeter_instance, audio_data, filename):
    """Exception handling test"""
    with patch.object(spleeter_instance, '_run_spleeter_command', side_effect=Exception("Test error")):
        progress_events = []
        async for event in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename
        ):
            progress_events.append(event)

        # error_update should be called
        error = any([isinstance(event, ErrorSSESchema) for event in progress_events])
        assert error


@pytest.mark.asyncio
async def test_separate_with_progress_temp_file_creation(spleeter_instance, audio_data, filename):
    """Temporary file creation test"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run, \
            patch.object(spleeter_instance, '_get_output_files') as mock_get_files, \
            patch.object(spleeter_instance.s3_uploader, 'upload_file') as mock_upload, \
            patch('builtins.open') as mock_open:

        mock_run.return_value = 0
        mock_get_files.return_value = {"vocals": Path("/tmp/vocals.mp3")}
        mock_upload.return_value = True

        mock_file = Mock()
        mock_open.return_value.__enter__ = Mock(return_value=mock_file)
        mock_open.return_value.__exit__ = Mock(return_value=None)

        async for _ in spleeter_instance.separate_with_progress(audio_data, filename):
            pass

        # Check that the file has been recorded
        mock_open.assert_called_once()
        mock_file.write.assert_called_once_with(audio_data)


def test_progress_tracker_integration(mock_s3_client):
    """Integration test with ProgressTracker"""
    spleeter = Spleeter(
        s3_client=mock_s3_client,
        s3_bucket="test-bucket"
    )

    assert hasattr(spleeter.progress_tracker, 'update_progress')
    assert hasattr(spleeter.progress_tracker, 'error_update')
    assert hasattr(spleeter.progress_tracker, 'result_update')


@pytest.mark.asyncio
async def test_s3_uploader_integration(spleeter_instance, audio_data, filename):
    """Integration test with S3Uploader"""
    with patch.object(spleeter_instance, '_run_spleeter_command') as mock_run, \
            patch.object(spleeter_instance, '_get_output_files') as mock_get_files, \
            patch.object(spleeter_instance.s3_uploader, 'upload_file') as mock_upload:

        mock_run.return_value = 0
        mock_get_files.return_value = {
            "vocals": Path("/tmp/vocals.mp3"),
            "accompaniments": Path("/tmp/accompaniments.mp3")
        }
        mock_upload.return_value = True

        async for _ in spleeter_instance.separate_with_progress(
                audio_bytes=audio_data,
                filename=filename,
                s3_output_prefix="test_prefix/"
        ):
            pass

        # Check that upload_file was called with the correct parameters
        assert mock_upload.call_count == 2
        calls = mock_upload.call_args_list
        assert any("test_prefix/" in str(call[0][1]) for call in calls)


@pytest.mark.asyncio
async def test_real_spleeter_processing(spleeter_instance, audio_data, filename):
    """
A test of the real audio separation process with verification of the stages of execution.
    Uses a real Spleeter call without mocks.
    """
    # Disabling mocks to real run Spleeter
    progress_events = []

    async for event in spleeter_instance.separate_with_progress(
            audio_bytes=audio_data,
            filename=filename,
            s3_output_prefix="test_prefix/",
    ):
        progress_events.append(event)

    # Checking that the process has passed the main stages
    assert len(progress_events) >= 5

    # Checking for progress events
    progress_events = [event for event in progress_events]

    # We check that the final result has been sent
    result = any([isinstance(event, ResultSSESchema) for event in progress_events])
    assert result
