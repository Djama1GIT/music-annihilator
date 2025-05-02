import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Union, Dict, Generator
from botocore.exceptions import ClientError


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
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket
        self.model = model
        self.codec = codec
        self.bitrate = bitrate
        self.logger = self._setup_logger() if enable_logging else None
        self._log(
            f"Initialized SpleeterSeparator with model={model}, codec={codec}, bitrate={bitrate}"
        )

    @staticmethod
    def _setup_logger() -> logging.Logger:
        logger = logging.getLogger("SpleeterSeparator")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("Logger setup complete")
        return logger

    def _log(self, message: str, level: str = "info"):
        if self.logger:
            getattr(self.logger, level)(message)

    def _upload_to_s3(self, file_path: Path, s3_key: str) -> bool:
        self._log(f"Attempting to upload file to S3: {file_path} -> {s3_key}")
        try:
            self.s3_client.upload_file(str(file_path), self.s3_bucket, s3_key)
            self._log(f"Successfully uploaded file to S3: {s3_key}")
            return True
        except ClientError as e:
            self._log(f"S3 upload error for {file_path}: {str(e)}", "error")
            return False
        except Exception as e:
            self._log(f"Unexpected error during S3 upload: {str(e)}", "error")
            return False

    def _run_spleeter_with_progress(
        self,
        input_path: Path,
        output_dir: Path,
    ) -> Generator[Dict[str, Union[int, str]], None, None]:
        """Генератор прогресса и результатов обработки"""
        try:
            self._log(f"Starting processing for file: {input_path}")
            self._log(f"Output directory: {output_dir}")

            # Этап 1: Подготовка (20%)
            yield {"progress": 20, "message": "File received, starting processing"}
            self._log("Preparation stage complete (20%)")

            # Create the output directory structure in advance

            self._log(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

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

            self._log(f"Preparing to run command: {' '.join(cmd)}")

            # Этап 2: Обработка началась (50%)
            yield {"progress": 50, "message": "Processing started"}
            self._log("Processing stage started (50%)")

            # Запускаем процесс
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self._log(f"Spleeter process started with PID: {process.pid}")

            # Ждем завершения
            process.wait()
            self._log(
                f"Spleeter process completed with return code: {process.returncode}"
            )

            # Этап 3: Обработка завершена (80%)
            yield {"progress": 80, "message": "Processing completed"}
            self._log("Processing stage completed (80%)")

            if process.returncode != 0:
                error = process.stderr.read()
                self._log(f"Spleeter processing failed with error: {error}", "error")
                yield {"progress": 100, "error": error}
                return

            # Находим результаты
            output_files = {}
            self._log(f"Searching for output files in: {output_dir}")
            for file in output_dir.iterdir():
                if file.is_file():
                    self._log(f"Found output file: {file.name}")
                    output_files[file.stem] = file

            self._log(f"Total output files found: {len(output_files)}")
            yield {
                "progress": 90,
                "message": "Files found",
                "files": {k: str(v) for k, v in output_files.items()}
            }
            return

        except subprocess.SubprocessError as e:
            self._log(f"Subprocess error during Spleeter execution: {str(e)}", "error")
            yield {"progress": 100, "error": str(e)}
            return
        except Exception as e:
            self._log(f"Unexpected error during processing: {str(e)}", "error")
            yield {"progress": 100, "error": str(e)}
            return

    def separate_with_progress(
        self, audio_bytes: bytes, filename: str, s3_output_prefix: str = ""
    ) -> Generator[Dict[str, Union[int, str, Dict[str, str]]], None, None]:
        """Генератор для SSE с прогрессом и результатами"""
        self._log(f"Starting separation process for file: {filename}")
        self._log(f"Output S3 prefix: {s3_output_prefix}")
        self._log(f"Audio data size: {len(audio_bytes)} bytes")

        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                temp_dir_path = Path(temp_dir)
                self._log(f"Created temporary directory: {temp_dir_path}")

                # Сохраняем входной файл
                input_path = temp_dir_path / filename
                self._log(f"Saving input file to: {input_path}")
                with open(input_path, "wb") as f:
                    f.write(audio_bytes)
                self._log(
                    f"Input file saved successfully. Size: {input_path.stat().st_size} bytes"
                )

                output_dir = temp_dir_path / "output"
                self._log(f"Creating output directory: {output_dir}")
                output_dir.mkdir()

                # Запускаем обработку с прогрессом
                progress_gen = self._run_spleeter_with_progress(input_path, output_dir)
                self._log("Spleeter process generator created")

                output_files = {}

                # Получаем обновления прогресса
                for progress_update in progress_gen:
                    print(0)
                    if "progress" in progress_update:
                        self._log(
                            f"Progress update: {progress_update['progress']}% - "
                            f"{progress_update.get('message', '')}"
                        )
                        yield progress_update
                    print(1)
                    if "error" in progress_update:
                        self._log(
                            f"Error in progress update: {progress_update['error']}",
                            "error",
                        )
                    print(2)
                    if "files" in progress_update:
                        print(3)
                        output_files = progress_update["files"]
                print(4)
                if output_files:
                    print(5)
                    self._log(
                        f"Processing completed with success, files={len(output_files)}"
                    )
                    yield {"progress": 90}
                else:
                    self._log("Processing failed, exiting", "error")
                    yield {"progress": 100, "error": "Processing failed"}
                    return

                # Загружаем в S3 и получаем ссылки
                self._log(f"Starting S3 upload for {len(output_files)} files")

                for stem, file_path in output_files.items():
                    s3_key = f"{s3_output_prefix}{input_path.stem}/{stem}.{self.codec}"
                    self._log(f"Uploading {stem} to S3: {s3_key}")
                    if self._upload_to_s3(file_path, s3_key):
                        self._log(f"Upload successful for {stem}")
                    else:
                        self._log(f"Upload failed for {stem}", "warning")
                        yield {"progress": 100, "error": f"Upload failed for {stem}"}
                        return

                self._log(f"Upload complete for {input_path.name}")

                # Финальный результат (100%)
                final_result = {
                    "progress": 100,
                    "message": "Processing complete",
                    "result": input_path.stem,
                }
                self._log(f"Yielding final result: {final_result}")
                yield final_result

            except IOError as e:
                self._log(f"File I/O error: {str(e)}", "error")
                yield {"progress": 100, "error": str(e)}
            except Exception as e:
                self._log(f"Unexpected error in separation process: {str(e)}", "error")
                yield {"progress": 100, "error": str(e)}
            finally:
                self._log("Cleaning up temporary directory")
