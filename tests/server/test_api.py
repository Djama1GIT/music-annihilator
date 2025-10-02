import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import UploadFile
from fastapi.responses import StreamingResponse

from src.server.api.v1.files import download_processed_file
from src.server.api.v1.processing import process_with_sse


class TestSpleeter:
    @pytest.mark.asyncio
    async def test_process_with_sse_success(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file,
            mock_spleeter_sse,
    ):
        """Successful audio processing test with SSE"""
        # Arrange
        mock_sse_generator = Mock(return_value=[b"test event data"])
        mock_spleeter_sse.sse_generator = mock_sse_generator

        with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse), \
                patch('src.server.api.v1.processing.uuid4', return_value="test-uuid-1234"), \
                patch('src.server.api.v1.processing.logger') as mock_logger:

            # Act
            response = await process_with_sse(
                file=mock_upload_file,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            assert isinstance(response, StreamingResponse)
            assert response.media_type == "text/event-stream"

            # Checking the logger calls
            mock_logger.info.assert_any_call("Starting audio processing for file: test_audio.mp3")
            mock_logger.info.assert_any_call("Processing audio... test_audio.mp3")
            mock_logger.info.assert_any_call("Generated unique filename: test-uuid-1234")
            mock_logger.debug.assert_any_call("Initializing SpleeterSeparator")
            mock_logger.debug.assert_any_call("Read file content, size: 18 bytes")

            # Checking the SSE generator call
            mock_sse_generator.assert_called_once_with(
                audio_bytes=b"test audio content",
                filename="test-uuid-1234"
            )

    @pytest.mark.asyncio
    async def test_process_with_sse_file_read_error(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file
    ):
        """File read error handling test"""
        # Arrange
        mock_upload_file.read.side_effect = Exception("File read error")

        with patch('src.server.api.v1.processing.logger') as mock_logger:
            # Act & Assert
            with pytest.raises(Exception, match="File read error"):
                await process_with_sse(
                    file=mock_upload_file,
                    s3=mock_s3_client,
                    settings=mock_settings
                )

            mock_logger.info.assert_called_once_with("Starting audio processing for file: test_audio.mp3")

    @pytest.mark.asyncio
    async def test_process_with_sse_spleeter_initialization_error(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file
    ):
        """SpleeterSSE initialization error handling test"""
        # Arrange
        with patch('src.server.api.v1.processing.SpleeterSSE') as mock_spleeter_class:
            mock_spleeter_class.side_effect = Exception("Spleeter initialization failed")

            # Act & Assert
            with pytest.raises(Exception, match="Spleeter initialization failed"):
                await process_with_sse(
                    file=mock_upload_file,
                    s3=mock_s3_client,
                    settings=mock_settings
                )

    @pytest.mark.asyncio
    async def test_process_with_sse_sse_generator_error(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file,
            mock_spleeter_sse
    ):
        """Error handling test in the SSE generator"""
        # Arrange
        mock_spleeter_sse.sse_generator.side_effect = Exception("SSE generator error")

        with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse):

            # Act & Assert
            with pytest.raises(Exception, match="SSE generator error"):
                await process_with_sse(
                    file=mock_upload_file,
                    s3=mock_s3_client,
                    settings=mock_settings
                )

    @pytest.mark.asyncio
    async def test_process_with_sse_async_file_read(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Asynchronous file reading test"""
        # Arrange
        mock_upload_file = Mock(spec=UploadFile)
        mock_upload_file.filename = "async_test.mp3"
        mock_upload_file.read = AsyncMock(return_value=b"async audio content")

        mock_sse_generator = Mock(return_value=[b"event data"])
        mock_spleeter_sse = Mock(sse_generator=mock_sse_generator)

        with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse), \
                patch('src.server.api.v1.processing.uuid4', return_value="async-uuid"):

            # Act
            response = await process_with_sse(
                file=mock_upload_file,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            assert isinstance(response, StreamingResponse)
            mock_upload_file.read.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_with_sse_different_file_types(
            self,
            mock_s3_client,
            mock_settings,
            mock_spleeter_sse
    ):
        """Test for processing different types of files"""
        # Arrange
        test_cases = [
            ("audio.wav", b"wav content"),
            ("music.mp3", b"mp3 content"),
            ("song.flac", b"flac content"),
            ("record.m4a", b"m4a content")
        ]

        mock_sse_generator = Mock(return_value=[b"event data"])
        mock_spleeter_sse.sse_generator = mock_sse_generator

        for filename, content in test_cases:
            with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse), \
                    patch('src.server.api.v1.processing.uuid4', return_value=f"uuid-{filename}"), \
                    patch('src.server.api.v1.processing.logger') as mock_logger:

                mock_upload_file = Mock(spec=UploadFile)
                mock_upload_file.filename = filename
                mock_upload_file.read = AsyncMock(return_value=content)

                # Act
                response = await process_with_sse(
                    file=mock_upload_file,
                    s3=mock_s3_client,
                    settings=mock_settings
                )

                # Assert
                assert isinstance(response, StreamingResponse)
                mock_logger.info.assert_any_call(f"Starting audio processing for file: {filename}")
                mock_logger.info.assert_any_call(f"Processing audio... {filename}")

    @pytest.mark.asyncio
    async def test_process_with_sse_uuid_generation(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file,
            mock_spleeter_sse
    ):
        """Unique file name generation test"""
        # Arrange
        mock_sse_generator = Mock(return_value=[b"event data"])
        mock_spleeter_sse.sse_generator = mock_sse_generator

        test_uuid = "unique-test-id-5678"

        with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse), \
                patch('src.server.api.v1.processing.uuid4', return_value=test_uuid), \
                patch('src.server.api.v1.processing.logger') as mock_logger:

            # Act
            response = await process_with_sse(
                file=mock_upload_file,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            assert isinstance(response, StreamingResponse)
            mock_logger.info.assert_any_call(f"Generated unique filename: {test_uuid}")

            # Check that the UUID is passed to the SSE generator
            mock_sse_generator.assert_called_once_with(
                audio_bytes=b"test audio content",
                filename=test_uuid
            )

    @pytest.mark.asyncio
    async def test_process_with_sse_generator(
            self,
            mock_s3_client,
            mock_settings,
            mock_upload_file,
            mock_spleeter_sse
    ):
        # Arrange
        mock_settings.S3_BUCKET = "custom-test-bucket"
        mock_sse_generator = Mock(return_value=[b"event data"])
        mock_spleeter_sse.sse_generator = mock_sse_generator

        with patch('src.server.api.v1.processing.SpleeterSSE', return_value=mock_spleeter_sse), \
                patch('src.server.api.v1.processing.uuid4', return_value="test-uuid"):

            # Act
            await process_with_sse(
                file=mock_upload_file,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            mock_spleeter_sse.sse_generator.assert_called()

    @pytest.fixture
    def mock_dependencies(self):
        """Ioc of all dependencies"""
        mock_file = Mock()
        mock_file.filename = "test.mp3"
        mock_file.read = AsyncMock(return_value=b"content")

        mock_s3 = Mock()
        mock_settings = Mock()
        mock_settings.S3_BUCKET = "test-bucket"

        return mock_file, mock_s3, mock_settings

    @pytest.mark.asyncio
    async def test_dependency_injection(self, mock_dependencies):
        """Dependency Injection test"""
        mock_file, mock_s3, mock_settings = mock_dependencies

        with patch('src.server.api.v1.processing.SpleeterSSE') as mock_spleeter_class, \
                patch('src.server.api.v1.processing.uuid4', return_value="test-uuid"):
            mock_spleeter_instance = Mock()
            mock_spleeter_instance.sse_generator = Mock(return_value=[b"data"])
            mock_spleeter_class.return_value = mock_spleeter_instance

            # Calling a function with dependency checks
            await process_with_sse(
                file=mock_file,
                s3=mock_s3,
                settings=mock_settings
            )

            # We check that the dependencies are transmitted correctly
            assert mock_spleeter_class.called
            mock_spleeter_class.assert_called_with(
                s3_client=mock_s3,
                s3_bucket="test-bucket"
            )

    @pytest.mark.asyncio
    async def test_async_file_operations(self, mock_dependencies):
        """Asynchronous file operations test"""
        mock_file, mock_s3, mock_settings = mock_dependencies

        with patch('src.server.api.v1.processing.SpleeterSSE') as mock_spleeter_class:
            mock_spleeter_instance = Mock()
            mock_spleeter_instance.sse_generator = Mock(return_value=[b"data"])
            mock_spleeter_class.return_value = mock_spleeter_instance

            # Calling the function
            await process_with_sse(
                file=mock_file,
                s3=mock_s3,
                settings=mock_settings
            )

            # Check that read was called as an asynchronous function
            mock_file.read.assert_awaited_once()


class TestS3Files:
    """Tests for file download routes from S3"""

    @pytest.mark.asyncio
    async def test_download_processed_file_success(
            self,
            mock_s3_client,
            mock_settings,
            mock_s3_response
    ):
        """Test of successful file download from S3"""
        # Arrange
        processed_filename = "job-123"
        result_filename = "vocals.mp3"
        expected_s3_key = f"processed/{processed_filename}/{result_filename}"

        mock_s3_client.get_object.return_value = mock_s3_response

        with patch('src.server.api.v1.files.logger') as mock_logger:
            # Act
            response = await download_processed_file(
                processed_filename=processed_filename,
                result_filename=result_filename,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            assert isinstance(response, StreamingResponse)
            assert response.media_type == "audio/mpeg"
            assert response.headers["Content-Disposition"] == "attachment; filename=job-123.mp3"
            assert response.headers["Content-Length"] == "1024"

            # Checking S3 calls
            mock_s3_client.get_object.assert_called_once_with(
                Bucket="test-bucket",
                Key=expected_s3_key
            )

            # Checking logging
            mock_logger.debug.assert_called_once_with(f"Constructed S3 key: {expected_s3_key}")
            mock_logger.info.assert_called_once_with("File successfully retrieved from S3")

    @pytest.mark.asyncio
    async def test_download_processed_file_different_formats(
            self,
            mock_s3_client,
            mock_settings,
            mock_s3_response
    ):
        """Test of downloading files of different formats"""
        # Arrange
        test_cases = [
            ("job-123", "vocals.wav", "job-123.wav"),
            ("uuid-456", "accompaniment.mp3", "uuid-456.mp3"),
            ("test-789", "bass.flac", "test-789.flac"),
            ("audio-999", "drums.m4a", "audio-999.m4a"),
        ]

        for processed_filename, result_filename, expected_filename in test_cases:
            mock_s3_client.get_object.return_value = mock_s3_response

            # Act
            response = await download_processed_file(
                processed_filename=processed_filename,
                result_filename=result_filename,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            expected_content_disposition = f"attachment; filename={expected_filename}"
            assert response.headers["Content-Disposition"] == expected_content_disposition

    @pytest.mark.asyncio
    async def test_download_processed_file_different_content_types(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Test of different types of content from S3"""
        # Arrange
        content_type_test_cases = [
            ("audio/wav", "job-123", "vocals.wav"),
            ("audio/mpeg", "job-456", "accompaniment.mp3"),
            ("audio/flac", "job-789", "bass.flac"),
            ("audio/mp4", "job-999", "drums.m4a"),
            ("application/octet-stream", "job-000", "unknown.xyz"),
        ]

        for content_type, processed_filename, result_filename in content_type_test_cases:
            mock_s3_response = {
                "Body": Mock(),
                "ContentType": content_type,
                "ContentLength": 2048
            }
            mock_s3_client.get_object.return_value = mock_s3_response

            # Act
            response = await download_processed_file(
                processed_filename=processed_filename,
                result_filename=result_filename,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            assert response.media_type == content_type
            assert response.headers["Content-Length"] == "2048"

    @pytest.mark.asyncio
    async def test_download_processed_file_large_file(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Large file upload test"""
        # Arrange
        processed_filename = "large-job"
        result_filename = "full_mix.wav"
        large_content_length = 1024 * 1024 * 100  # 100MB

        mock_s3_response = {
            "Body": Mock(),
            "ContentType": "audio/wav",
            "ContentLength": large_content_length
        }
        mock_s3_client.get_object.return_value = mock_s3_response

        # Act
        response = await download_processed_file(
            processed_filename=processed_filename,
            result_filename=result_filename,
            s3=mock_s3_client,
            settings=mock_settings
        )

        # Assert
        assert response.headers["Content-Length"] == str(large_content_length)

    @pytest.mark.asyncio
    async def test_download_processed_file_s3_bucket_config(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Test of using the correct S3 bucket"""
        # Arrange
        processed_filename = "job-123"
        result_filename = "vocals.mp3"
        expected_bucket = "custom-bucket-name"

        mock_settings.S3_BUCKET = expected_bucket
        mock_s3_response = {
            "Body": Mock(),
            "ContentType": "audio/mpeg",
            "ContentLength": 1024
        }
        mock_s3_client.get_object.return_value = mock_s3_response

        # Act
        await download_processed_file(
            processed_filename=processed_filename,
            result_filename=result_filename,
            s3=mock_s3_client,
            settings=mock_settings
        )

        # Assert
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=expected_bucket,
            Key=f"processed/{processed_filename}/{result_filename}"
        )

    @pytest.mark.asyncio
    async def test_download_processed_file_special_characters_in_filenames(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Test of handling special characters in file names"""
        # Arrange
        test_cases = [
            ("job_with_underscores", "file_with-dashes.mp3"),
            ("job.with.dots", "file with spaces.wav"),
            ("job@with#special$chars", "mixed_case_FILE.MP3"),
        ]

        mock_s3_response = {
            "Body": Mock(),
            "ContentType": "audio/mpeg",
            "ContentLength": 1024
        }
        mock_s3_client.get_object.return_value = mock_s3_response

        for processed_filename, result_filename in test_cases:
            mock_s3_client.get_object.reset_mock()

            # Act
            response = await download_processed_file(
                processed_filename=processed_filename,
                result_filename=result_filename,
                s3=mock_s3_client,
                settings=mock_settings
            )

            # Assert
            expected_s3_key = f"processed/{processed_filename}/{result_filename}"
            mock_s3_client.get_object.assert_called_once_with(
                Bucket="test-bucket",
                Key=expected_s3_key
            )

            # Check that the extension is being extracted correctly
            file_extension = result_filename.split('.')[-1]
            expected_filename = f"{processed_filename}.{file_extension}"
            expected_content_disposition = f"attachment; filename={expected_filename}"
            assert response.headers["Content-Disposition"] == expected_content_disposition

    @pytest.mark.asyncio
    async def test_download_processed_file_streaming(
            self,
            mock_s3_client,
            mock_settings
    ):
        """Test that the response is indeed a streaming response"""
        # Arrange
        processed_filename = "stream-test"
        result_filename = "vocals.mp3"

        # Creating a mock stream object
        mock_stream = AsyncMock()
        mock_s3_response = {
            "Body": mock_stream,
            "ContentType": "audio/mpeg",
            "ContentLength": 1024
        }
        mock_s3_client.get_object.return_value = mock_s3_response

        # Act
        response = await download_processed_file(
            processed_filename=processed_filename,
            result_filename=result_filename,
            s3=mock_s3_client,
            settings=mock_settings
        )

        # Assert
        assert isinstance(response, StreamingResponse)
        assert response.body_iterator == mock_stream  # Check that the correct stream has been transmitted
