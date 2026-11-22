"""
Backend abstraction and platform-specific speech engines for UniversalSpeech.
"""
from .base import BaseBackend
from .windows import WindowsBackend
from .linux import LinuxBackend

__all__ = ["BaseBackend", "WindowsBackend", "LinuxBackend"]
