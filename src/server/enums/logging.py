from enum import Enum


class LoggingLevelsEnum(Enum):
    """
    Enumeration of standard logging levels with their string representations.

    This enum provides a type-safe way to work with Python logging levels and their
    string values. It includes all standard logging levels plus common aliases.

    The enum values correspond to the string representations used by Python's built-in
    logging module, ensuring compatibility with logging configuration files and APIs
    that expect string level names.

    Parameters:
        CRITICAL: Critical error level (highest severity)
        FATAL: Alias for CRITICAL level
        ERROR: Error level
        WARN: Warning level (alias for WARNING)
        WARNING: Warning level
        INFO: Informational level
        DEBUG: Debug level (lowest severity for development)
        NOTSET: Special level indicating all messages should be logged
    """

    CRITICAL = "critical"
    FATAL = "fatal"
    ERROR = "error"
    WARN = "warning"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"
    NOTSET = "notset"

    def __repr__(self):
        """
        Returns the string representation of the logging level.

        Returns:
            str: The string value of the enum member.
        """
        return self.value
