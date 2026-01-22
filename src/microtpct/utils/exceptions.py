"""
MicroTPCT custom exceptions.

Provides a hierarchy of exceptions for better error handling and diagnosis.
"""


class MicroTPCTError(Exception):
    """Base class for all MicroTPCT exceptions."""
    pass


class InvalidInputError(MicroTPCTError):
    """Raised when input files or data are invalid."""
    pass


class AlignmentError(MicroTPCTError):
    """Raised when alignment step fails."""
    pass


class ConfigError(MicroTPCTError):
    """Raised when configuration is wrong or missing."""
    pass


class DatabaseError(MicroTPCTError):
    """Raised when database operations fail."""
    pass


class FormatError(MicroTPCTError):
    """Raised when file format is incorrect."""
    pass
