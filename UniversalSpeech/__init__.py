"""
UniversalSpeech: Python bindings and high-level SDK for the UniversalSpeech library.

This library provides a unified Python interface for speech synthesis and
braille displays across multiple screen readers and native speech engines
on Windows (32-bit and 64-bit).

Based on the original UniversalSpeech C library created by Quentin Cosendey:
https://github.com/qtnc/UniversalSpeech
"""

from .constants import (
    VOLUME, VOLUME_MAX, VOLUME_MIN, VOLUME_SUPPORTED,
    RATE, RATE_MAX, RATE_MIN, RATE_SUPPORTED,
    PITCH, PITCH_MAX, PITCH_MIN, PITCH_SUPPORTED,
    INFLECTION, INFLECTION_MAX, INFLECTION_MIN, INFLECTION_SUPPORTED,
    PAUSED, PAUSE_SUPPORTED,
    BUSY, BUSY_SUPPORTED,
    WAIT, WAIT_SUPPORTED,
    ENABLE_NATIVE_SPEECH,
    VOICE,
    LANGUAGE,
    SUBENGINE,
    ENGINE,
    ENGINE_AVAILABLE,
    AUTO_ENGINE,
    USER_PARAM,
    SpeechParam,
    ScreenReaderId,
)
from .exceptions import (
    UniversalSpeechError,
    DLLFileNotFoundError,
    UnsupportedError,
    EngineError,
    VoiceError,
)
from .voices import Voice
from .screen_readers import ScreenReaderInfo
from .loader import Loader
from .core import UniversalSpeech

__version__ = "3.0.0"

__all__ = [
    # Core class, data models, and loader
    "UniversalSpeech",
    "Voice",
    "ScreenReaderInfo",
    "Loader",
    # Constants
    "VOLUME",
    "VOLUME_MAX",
    "VOLUME_MIN",
    "VOLUME_SUPPORTED",
    "RATE",
    "RATE_MAX",
    "RATE_MIN",
    "RATE_SUPPORTED",
    "PITCH",
    "PITCH_MAX",
    "PITCH_MIN",
    "PITCH_SUPPORTED",
    "INFLECTION",
    "INFLECTION_MAX",
    "INFLECTION_MIN",
    "INFLECTION_SUPPORTED",
    "PAUSED",
    "PAUSE_SUPPORTED",
    "BUSY",
    "BUSY_SUPPORTED",
    "WAIT",
    "WAIT_SUPPORTED",
    "ENABLE_NATIVE_SPEECH",
    "VOICE",
    "LANGUAGE",
    "SUBENGINE",
    "ENGINE",
    "ENGINE_AVAILABLE",
    "AUTO_ENGINE",
    "USER_PARAM",
    "SpeechParam",
    "ScreenReaderId",
    # Exceptions
    "UniversalSpeechError",
    "DLLFileNotFoundError",
    "UnsupportedError",
    "EngineError",
    "VoiceError",
]
