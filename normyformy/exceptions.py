"""Custom Exceptions.

This module defines custom exception classes used throughout the application.

NOTE: This module is a modified version of Copcon module: copcon/exceptions.py
"""


class FileReadError(Exception):
    """Exception raised when a file cannot be read."""

    pass


class ClipboardError(Exception):
    """Exception raised when clipboard operations fail."""

    pass
