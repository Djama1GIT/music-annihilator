import asyncio
import tempfile
from pathlib import Path
from typing import Dict, AsyncGenerator, Optional

from src.server.annihilator.progress_tracker import ProgressTracker
from src.server.enums.logging import LoggingLevelsEnum
from src.server.enums.progress import AnnihilationProgressEnum
from src.server.logger import logger
from src.server.schemas.annihilator_sse import ProgressSSESchema
from src.server.services.s3.uploader import S3Uploader


class Spleeter:
    """
    A class for separating audio tracks using Spleeter with progress tracking and S3 upload capabilities.

    This class provides functionality to separate audio files into stems using the Spleeter library,
    track progress through different stages, and upload results to S3 storage.

    Parameters:
        s3_client: Initialized S3 client for file uploads
        s3_bucket (str): Name of the S3 bucket for uploads
        model (str): Spleeter model to use (default: "2stems")
        codec (str): Output audio codec (default: "mp3")
        bitrate (str): Output audio bitrate (default: "192k")
        enable_logging (bool): Whether to enable logging (default: True)
    """

    def __init__(
        self,
        s3_client,
        s3_bucket: str,
        model: str = "2stems",
        codec: str = "mp3",
        bitrate: str = "192k",
        enable_logging: bool = True,
    ):
        """Initialize the Spleeter separator with configuration and dependencies."""
        self.model = model
        self.codec = codec
        self.bitrate = bitrate
        self.logger = logger if enable_logging else None
        self.s3_uploader = S3Uploader(s3_client, s3_bucket, self.logger)
        self.progress_tracker = ProgressTracker(self.logger)

        self._log(
            f"Initialized SpleeterSeparator with model={model}, "
            f"codec={codec}, bitrate={bitrate}"
        )

    def _log(
        self,
        message: str,
        *,
        level: LoggingLevelsEnum = LoggingLevelsEnum.INFO,
        exc_info: bool = False,
    ) -> None:
        """
        Internal logging helper with class name prefix.

        Parameters:
            message (str): Message to log
            level (LoggingLevelsEnum): Logging level (default: INFO)
            exc_info (bool): Whether to include exception info (default: False)
        """
        if self.logger:
            getattr(self.logger, level.value)(
                f"{self.__class__.__name__}: {message}",
                exc_info=exc_info,
            )

    async def _run_spleeter_command(self, input_path: Path, output_dir: Path) -> Optional[int]:
        """
        Execute the spleeter command asynchronously and return the exit code with full logging.

        Parameters:
            input_path (Path): Path to input audio file
            output_dir (Path): Directory to save output stems

        Returns:
            int: Process exit code (0 for success)

        Raises:
            subprocess.SubprocessError: If command execution fails
        """
        cmd = [
            "spleeter",
            "separate",
            "-p",
            f"spleeter:{self.model}",
            "-c",
            self.codec,
            "-b",
            self.bitrate,
            "-o",
            str(output_dir),
            "-f",
            "{instrument}.{codec}",
            str(input_path),
            "--verbose"
        ]

        self._log(f"Starting separation process")
        self._log(f"Input file: {input_path}")
        self._log(f"Output directory: {output_dir}")
        self._log(f"Model: {self.model}")
        self._log(f"Codec: {self.codec}")
        self._log(f"Bitrate: {self.bitrate}")
        self._log(f"Full command: {' '.join(cmd)}")

        try:
            # Create subprocess and run asynchronously
            self._log("Creating subprocess...")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._log(f"Subprocess created with PID: {process.pid}")

            # Log stdout and stderr in real-time
            async def log_stream(stream, stream_name):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    self._log(f"{stream_name}: {line.decode().strip()}")

            # Create tasks for logging both streams
            stdout_task = asyncio.create_task(log_stream(process.stdout, "STDOUT"))
            stderr_task = asyncio.create_task(log_stream(process.stderr, "STDERR"))

            self._log("Waiting for process completion...")
            return_code = await process.wait()
            self._log(f"Process completed with return code: {return_code}")

            # Wait for all output to be logged
            await asyncio.wait([stdout_task, stderr_task])

            if return_code != 0:
                self._log("Warning: Process finished with non-zero exit code")
            else:
                self._log("Separation completed successfully")

            return return_code

        except Exception as e:
            self._log(f"Error during processing: {str(e)}")
            raise

    @staticmethod
    def _get_output_files(output_dir: Path) -> Dict[str, Path]:
        """
        Collect and return the output files from the processing directory.

        Parameters:
            output_dir (Path): Directory containing processed files

        Returns:
            Dict[str, Path]: Mapping of stem names to file paths

        Raises:
            FileNotFoundError: If output directory doesn't exist
        """
        return {file.stem: file for file in output_dir.iterdir() if file.is_file()}

    async def separate_with_progress(
        self,
        audio_bytes: bytes,
        filename: str,
        s3_output_prefix: str = "",
    ) -> AsyncGenerator[ProgressSSESchema, None]:
        """
        Separate audio file with progress updates via Server-Sent Events (SSE).

        Parameters:
            audio_bytes (bytes): Audio file content as bytes
            filename (str): Original filename (used for naming outputs)
            s3_output_prefix (str): Prefix for S3 upload paths (default: "")

        Yields:
            Union[ProgressSSESchema, ErrorSSESchema, ResultSSESchema]: SSE events for:
                - Progress updates
                - Error notifications
                - Final results

        Raises:
            Exception: For any unexpected processing errors
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                temp_dir_path = Path(temp_dir)
                input_path = temp_dir_path / filename

                # Save input file
                with open(input_path, "wb") as f:
                    f.write(audio_bytes)

                # Process with Spleeter
                output_dir = temp_dir_path / "output"
                output_dir.mkdir()

                yield self.progress_tracker.update_progress(
                    progress=AnnihilationProgressEnum.STARTING_WORK,
                    message="File received, starting processing",
                )

                yield self.progress_tracker.update_progress(
                    progress=AnnihilationProgressEnum.WORK_STARTED,
                    message="Processing in progress",
                )

                # Run command asynchronously
                return_code = await self._run_spleeter_command(input_path, output_dir)
                if return_code != 0:
                    yield self.progress_tracker.error_update(
                        error="Spleeter processing failed",
                    )
                    return

                yield self.progress_tracker.update_progress(
                    progress=AnnihilationProgressEnum.WORK_COMPLETED,
                    message="Processing completed",
                )

                # Handle output files
                output_files = self._get_output_files(output_dir)
                if not output_files:
                    yield self.progress_tracker.error_update(
                        error="No output files generated",
                    )
                    return

                yield self.progress_tracker.update_progress(
                    progress=AnnihilationProgressEnum.FINALIZING_WORK,
                    message="Files found",
                )

                # Upload to S3
                for stem, file_path in output_files.items():
                    s3_key = f"{s3_output_prefix}{input_path.stem}/{stem}.{self.codec}"
                    if not self.s3_uploader.upload_file(file_path, s3_key):
                        yield self.progress_tracker.error_update(
                            error=f"Upload failed for {stem}",
                        )
                        return

                yield self.progress_tracker.result_update(
                    message="Processing complete",
                    result=input_path.stem,
                )

            except Exception as e:
                self._log(
                    message=f"Error during processing: {str(e)}",
                    level=LoggingLevelsEnum.ERROR,
                    exc_info=True,
                )
                yield self.progress_tracker.error_update(error=str(e))
