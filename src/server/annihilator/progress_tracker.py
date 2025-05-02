from typing import Dict, Union


class ProgressTracker:
    def __init__(self, logger=None):
        self.logger = logger

    def _log(self, message: str, level: str = "info"):
        if self.logger:
            getattr(self.logger, level)(f"{__class__.__name__}: {message}")

    def update_progress(self, progress: int, message: str = "", **kwargs) -> Dict[str, Union[int, str]]:
        """Create a progress update dictionary."""
        update = {"progress": progress, "message": message}
        update.update(kwargs)
        self._log(f"Progress: {progress}% - {message}")

        return update

    def error_update(self, error: str) -> Dict[str, Union[int, str]]:
        """Create an error update dictionary."""
        self._log(f"Error: {error}", "error")

        return {"progress": 100, "error": error}
