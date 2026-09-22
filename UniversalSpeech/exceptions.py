"""
Exceptions for the UniversalSpeech package.
"""


class UniversalSpeechError(Exception):
    """Base exception class for all UniversalSpeech errors."""
    pass


class DLLFileNotFoundError(UniversalSpeechError):
    """Raised when one or more required DLL files are missing."""
    pass


class UnsupportedError(UniversalSpeechError):
    """Raised when an operation or parameter is not supported by the current speech engine."""
    pass


class EngineError(UniversalSpeechError):
    """Raised when an invalid or unavailable speech engine is requested."""
    pass


class VoiceError(UniversalSpeechError):
    """Raised when an invalid voice is requested or voices are not supported."""
    pass


__all__ = [
    "UniversalSpeechError",
    "DLLFileNotFoundError",
    "UnsupportedError",
    "EngineError",
    "VoiceError",
]
