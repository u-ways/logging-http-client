from __future__ import annotations
from enum import Enum


class LogLevel(Enum):
    """
    An Enum representing the log levels that are supported by the logging module.
    """

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
