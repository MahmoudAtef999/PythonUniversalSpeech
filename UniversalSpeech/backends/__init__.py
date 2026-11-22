"""
Backend abstraction and platform-specific speech engines for UniversalSpeech.
"""
from .base import BaseBackend
from .windows import WindowsBackend

__all__ = ["BaseBackend", "WindowsBackend"]
