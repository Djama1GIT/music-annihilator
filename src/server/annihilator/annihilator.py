import subprocess
import tempfile
from pathlib import Path
from typing import Union, Dict, Generator

from src.server.annihilator.progress_tracker import ProgressTracker
from src.server.services.s3.uploader import S3Uploader
from src.server.logger import logger


class SpleeterSeparator:
    def __init__(
        self,
        s3_client,
        s3_bucket: str,
        model: str = "2stems",
        codec: str = "mp3",
        bitrate: str = "192k",
        enable_logging: bool = True,
    ):
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

    def _log(self, message: str, level: str = "info"):
        if self.logger:
            getattr(self.logger, level)(f"{__class__.__name__}: {message}")

    def _run_spleeter_command(self, input_path: Path, output_dir: Path) -> int:
        """Execute the spleeter command and return the exit code."""
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
        ]

        self._log(f"Executing command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        process.wait()
        return process.returncode

    @staticmethod
    def _get_output_files(output_dir: Path) -> Dict[str, Path]:
        """Collect and return the output files from the processing directory."""
        output_files = {}
        for file in output_dir.iterdir():
            if file.is_file():
                output_files[file.stem] = file
        return output_files

    def separate_with_progress(
        self, audio_bytes: bytes, filename: str, s3_output_prefix: str = ""
    ) -> Generator[Dict[str, Union[int, str, Dict[str, str]]], None, None]:
        """Generator for SSE with progress and results"""
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
                    progress=50,
                    message="File received, starting processing"
                )

                return_code = self._run_spleeter_command(input_path, output_dir)
                if return_code != 0:
                    yield self.progress_tracker.error_update(
                        error="Spleeter processing failed"
                    )
                    return

                yield self.progress_tracker.update_progress(
                    progress=80,
                    message="Processing completed",
                )

                # Handle output files
                output_files = self._get_output_files(output_dir)
                if not output_files:
                    yield self.progress_tracker.error_update(
                        "No output files generated"
                    )
                    return

                yield self.progress_tracker.update_progress(
                    progress=90,
                    message="Files found",
                    files={k: str(v) for k, v in output_files.items()},
                )

                # Upload to S3
                for stem, file_path in output_files.items():
                    s3_key = f"{s3_output_prefix}{input_path.stem}/{stem}.{self.codec}"
                    if not self.s3_uploader.upload_file(file_path, s3_key):
                        yield self.progress_tracker.error_update(
                            f"Upload failed for {stem}"
                        )
                        return

                yield self.progress_tracker.update_progress(
                    progress=100,
                    message="Processing complete",
                    result=input_path.stem,
                )

            except Exception as e:
                yield self.progress_tracker.error_update(str(e))
