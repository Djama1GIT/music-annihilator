from typing import AsyncGenerator

from src.server.annihilator.spleeter import Spleeter
from src.server.enums.logger import LoggerLevelsEnum


class SpleeterSSE(Spleeter):
    """
    A Spleeter implementation that generates Server-Sent Events (SSE) for real-time progress updates.

    This class extends the base Spleeter functionality to provide an asynchronous generator
    that yields SSE-formatted messages for tracking audio separation progress.

    Inherits:
        Spleeter: Base audio separation functionality
    """

    async def sse_generator(
        self, audio_bytes: bytes, filename: str
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronously generate Server-Sent Events for audio processing progress.

        Parameters:
            audio_bytes (bytes): The audio file content to process
            filename (str): Original filename (used for naming outputs)

        Yields:
            str: SSE-formatted messages including:
                - Progress updates
                - Error notifications
                - Final results
                - Stream closure

        Raises:
            Exception: Propagates any errors from the processing pipeline
        """
        try:
            self._log(
                message="Starting SSE event generator",
                level=LoggerLevelsEnum.DEBUG,
            )

            # Process audio and generate progress updates
            for sse_update in self.separate_with_progress(
                audio_bytes=audio_bytes,
                filename=filename,
                s3_output_prefix="processed/",
            ):
                self._log(
                    message=f"Yielding progress update: {sse_update}",
                    level=LoggerLevelsEnum.DEBUG,
                )
                yield f"data: {sse_update.model_dump_json(exclude_none=True)}\n\n"

            self._log("Audio processing completed successfully")

        except Exception as exc:
            self._log(
                message=f"Error during audio processing: {str(exc)}",
                level=LoggerLevelsEnum.ERROR,
                exc_info=True,
            )
            yield f'data: {{"error": "{str(exc)}"}}\n\n'

        finally:
            self._log(
                message="Closing SSE stream",
                level=LoggerLevelsEnum.DEBUG,
            )
            yield "event: close\n\n"
