"""
Core UniversalSpeech facade and interface.
"""
import sys
from typing import Optional, Dict, Any, Union, List, Tuple
from .backends.base import BaseBackend
from .exceptions import PlatformError
from .voices import Voice
from .screen_readers import ScreenReaderInfo
from .constants import (
    ScreenReaderId,
    VOLUME, VOLUME_MAX, VOLUME_MIN, VOLUME_SUPPORTED,
    RATE, RATE_MAX, RATE_MIN, RATE_SUPPORTED,
    PITCH, PITCH_MAX, PITCH_MIN, PITCH_SUPPORTED,
    INFLECTION, INFLECTION_MAX, INFLECTION_MIN, INFLECTION_SUPPORTED,
)


class UniversalSpeech(BaseBackend):
    """
    UniversalSpeech facade providing a unified, cross-platform interface for speech
    synthesis and braille displays across Windows, Linux, and macOS.
    """

    def __init__(self, backend: Optional[BaseBackend] = None, stop_on_exit: bool = False) -> None:
        """
        Initialize UniversalSpeech.

        Parameters:
            backend (Optional[BaseBackend]): Optional explicit backend instance.
                If None, the backend is automatically selected according to the OS platform.
            stop_on_exit (bool): Whether to stop ongoing speech when exiting a context manager
                (`with UniversalSpeech():`). Defaults to False so ongoing speech (e.g. from
                screen readers) is not abruptly cut off when exiting the block.
        """
        self._stop_on_exit = stop_on_exit
        if backend is not None:
            self._backend = backend
        elif sys.platform == "win32":
            from .backends.windows import WindowsBackend
            self._backend = WindowsBackend()
        elif sys.platform.startswith("linux"):
            from .backends.linux import LinuxBackend
            self._backend = LinuxBackend()
        elif sys.platform == "darwin":
            from .backends.macos import MacOSBackend
            self._backend = MacOSBackend()
        else:
            raise PlatformError(f"Unsupported operating system: {sys.platform}")

    @property
    def stop_on_exit(self) -> bool:
        """Whether speech is stopped on context manager exit."""
        return self._stop_on_exit

    @stop_on_exit.setter
    def stop_on_exit(self, value: bool) -> None:
        self._stop_on_exit = bool(value)

    @property
    def backend(self) -> BaseBackend:
        """The underlying active platform backend instance."""
        return self._backend

    @property
    def _UniversalSpeech__uspeech(self) -> Any:
        """Access underlying ctypes CDLL for Windows backward compatibility."""
        return getattr(self._backend, "uspeech", None)

    @_UniversalSpeech__uspeech.setter
    def _UniversalSpeech__uspeech(self, value: Any) -> None:
        if hasattr(self._backend, "uspeech"):
            self._backend.__dict__["_WindowsBackend__uspeech"] = value

    def __enter__(self) -> "UniversalSpeech":
        """Support context manager entry: `with UniversalSpeech() as speech:`."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support context manager exit without abruptly silencing ongoing speech unless stop_on_exit=True."""
        if self._stop_on_exit:
            self.stop()
        self.close()

    def close(self) -> None:
        """Clean up resources without forcibly stopping active speech."""
        self._backend.close()

    def __repr__(self) -> str:
        return f"<UniversalSpeech backend={self._backend.__class__.__name__} engine={self.engine_used!r}, reader={self.current_screen_reader_name!r}>"

    def __str__(self) -> str:
        return f"UniversalSpeech({self.engine_used or 'None'})"

    def __getattr__(self, name: str) -> Any:
        """Forward any attribute not explicitly declared to the underlying backend."""
        return getattr(self._backend, name)

    def say(self, msg: str, interrupt: bool = True) -> int:
        return self._backend.say(msg, interrupt=interrupt)

    def say_a(self, msg: Union[str, bytes], interrupt: bool = True) -> int:
        return self._backend.say_a(msg, interrupt=interrupt)

    sayA = say_a

    def braille(self, msg: str) -> int:
        return self._backend.braille(msg)

    def speech(self, msg: str, interrupt: bool = True) -> None:
        self._backend.speech(msg, interrupt=interrupt)

    def speech_a(self, msg: Union[str, bytes], interrupt: bool = True) -> None:
        self._backend.speech_a(msg, interrupt=interrupt)

    def stop(self) -> int:
        return self._backend.stop()

    def get_value(self, what: int) -> int:
        return self._backend.get_value(what)

    def set_value(self, what: int, value: int) -> int:
        return self._backend.set_value(what, value)

    def get_string(self, what: int) -> Optional[str]:
        return self._backend.get_string(what)

    def set_string(self, what: int, value: str) -> int:
        return self._backend.set_string(what, value)

    def enable_native_speech(self, enabled: bool = True) -> None:
        self._backend.enable_native_speech(enabled)

    @property
    def engine_used(self) -> str:
        return self._backend.engine_used

    def set_engine(self, engine: Union[str, int, ScreenReaderId, ScreenReaderInfo]) -> None:
        self._backend.set_engine(engine)

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
        return self._backend.get_engines()

    def reset_engine(self) -> None:
        self._backend.reset_engine()

    def say_ssml(self, ssml: str) -> bool:
        return self._backend.say_ssml(ssml)

    @property
    def is_busy(self) -> bool:
        return self._backend.is_busy

    @property
    def busy_supported(self) -> bool:
        return self._backend.busy_supported

    @property
    def is_paused(self) -> bool:
        return self._backend.is_paused

    @property
    def pause_supported(self) -> bool:
        return self._backend.pause_supported

    def pause(self, paused: bool = True) -> None:
        self._backend.pause(paused)

    def resume(self) -> None:
        self._backend.resume()

    @property
    def wait_supported(self) -> bool:
        return self._backend.wait_supported

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        return self._backend.wait(timeout_ms)

    @property
    def voice_supported(self) -> bool:
        return self._backend.voice_supported

    def get_voice(self) -> Optional[Voice]:
        return self._backend.get_voice()

    def set_voice(self, voice: Union[Voice, int, str]) -> None:
        self._backend.set_voice(voice)

    @property
    def current_voice(self) -> Optional[Voice]:
        return self._backend.current_voice

    @current_voice.setter
    def current_voice(self, voice: Union[Voice, int, str]) -> None:
        self.set_voice(voice)

    def get_voices(self) -> List[Voice]:
        return self._backend.get_voices()

    # Rate
    @property
    def rate_supported(self) -> bool:
        if "get_value" in self.__dict__:
            return bool(self.get_value(RATE_SUPPORTED))
        return self._backend.rate_supported

    def get_rate(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(RATE)
        return self._backend.get_rate()

    def set_rate(self, rate: int, min_rate: Optional[int] = None, max_rate: Optional[int] = None) -> None:
        if "set_value" in self.__dict__:
            self.set_value(RATE, rate)
            return
        self._backend.set_rate(rate, min_rate=min_rate, max_rate=max_rate)

    @property
    def rate(self) -> int:
        return self.get_rate()

    @rate.setter
    def rate(self, value: int) -> None:
        self.set_rate(value)

    @property
    def rate_min(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(RATE_MIN)
        return self._backend.rate_min

    @property
    def rate_max(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(RATE_MAX)
        return self._backend.rate_max

    @property
    def rate_range(self) -> Tuple[int, int]:
        return (self.rate_min, self.rate_max)

    # Volume
    @property
    def volume_supported(self) -> bool:
        if "get_value" in self.__dict__:
            return bool(self.get_value(VOLUME_SUPPORTED))
        return self._backend.volume_supported

    def get_volume(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(VOLUME)
        return self._backend.get_volume()

    def set_volume(self, volume: int, min_volume: Optional[int] = None, max_volume: Optional[int] = None) -> None:
        if "set_value" in self.__dict__:
            self.set_value(VOLUME, volume)
            return
        self._backend.set_volume(volume, min_volume=min_volume, max_volume=max_volume)

    @property
    def volume(self) -> int:
        return self.get_volume()

    @volume.setter
    def volume(self, value: int) -> None:
        self.set_volume(value)

    @property
    def volume_min(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(VOLUME_MIN)
        return self._backend.volume_min

    @property
    def volume_max(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(VOLUME_MAX)
        return self._backend.volume_max

    @property
    def volume_range(self) -> Tuple[int, int]:
        return (self.volume_min, self.volume_max)

    # Pitch
    @property
    def pitch_supported(self) -> bool:
        if "get_value" in self.__dict__:
            return bool(self.get_value(PITCH_SUPPORTED))
        return self._backend.pitch_supported

    def get_pitch(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(PITCH)
        return self._backend.get_pitch()

    def set_pitch(self, pitch: int, min_pitch: Optional[int] = None, max_pitch: Optional[int] = None) -> None:
        if "set_value" in self.__dict__:
            self.set_value(PITCH, pitch)
            return
        self._backend.set_pitch(pitch, min_pitch=min_pitch, max_pitch=max_pitch)

    @property
    def pitch(self) -> int:
        return self.get_pitch()

    @pitch.setter
    def pitch(self, value: int) -> None:
        self.set_pitch(value)

    @property
    def pitch_min(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(PITCH_MIN)
        return self._backend.pitch_min

    @property
    def pitch_max(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(PITCH_MAX)
        return self._backend.pitch_max

    @property
    def pitch_range(self) -> Tuple[int, int]:
        return (self.pitch_min, self.pitch_max)

    # Inflection
    @property
    def inflection_supported(self) -> bool:
        if "get_value" in self.__dict__:
            return bool(self.get_value(INFLECTION_SUPPORTED))
        return self._backend.inflection_supported

    def get_inflection(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(INFLECTION)
        return self._backend.get_inflection()

    def set_inflection(self, inflection: int, min_inflection: Optional[int] = None, max_inflection: Optional[int] = None) -> None:
        if "set_value" in self.__dict__:
            self.set_value(INFLECTION, inflection)
            return
        self._backend.set_inflection(inflection, min_inflection=min_inflection, max_inflection=max_inflection)

    @property
    def inflection(self) -> int:
        return self.get_inflection()

    @inflection.setter
    def inflection(self, value: int) -> None:
        self.set_inflection(value)

    @property
    def inflection_min(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(INFLECTION_MIN)
        return self._backend.inflection_min

    @property
    def inflection_max(self) -> int:
        if "get_value" in self.__dict__:
            return self.get_value(INFLECTION_MAX)
        return self._backend.inflection_max

    @property
    def inflection_range(self) -> Tuple[int, int]:
        return (self.inflection_min, self.inflection_max)

    # Screen Readers & Engines
    @property
    def current_screen_reader_name(self) -> str:
        return self._backend.current_screen_reader_name

    @property
    def current_screen_reader_id(self) -> int:
        return self._backend.current_screen_reader_id

    def get_supported_screen_readers(self) -> List[str]:
        return self._backend.get_supported_screen_readers()

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        return self._backend.get_screen_readers()

    def _is_reader_available(self, reader_id: int, name: str) -> bool:
        return self._backend._is_reader_available(reader_id, name)

    # Windows Screen Reader Checks
    def nvda_is_available(self) -> bool:
        return self._backend.nvda_is_available()

    def jaws_is_available(self) -> bool:
        return self._backend.jaws_is_available()

    def sapi_is_available(self) -> bool:
        return self._backend.sapi_is_available()

    def system_access_is_available(self) -> bool:
        return self._backend.system_access_is_available()

    def supernova_is_available(self) -> bool:
        return self._backend.supernova_is_available()

    def window_eyes_is_available(self) -> bool:
        return self._backend.window_eyes_is_available()

    def cobra_is_available(self) -> bool:
        return self._backend.cobra_is_available()

    def zoomtext_is_available(self) -> bool:
        return self._backend.zoomtext_is_available()

    def narrator_is_available(self) -> bool:
        return self._backend.narrator_is_available()

    def zdsr_is_available(self) -> bool:
        return self._backend.zdsr_is_available()

    # Versions
    def nvda_get_version(self) -> Optional[str]:
        return self._backend.nvda_get_version()

    def jfw_get_version(self) -> Optional[str]:
        return self._backend.jfw_get_version()

    def jaws_get_version(self) -> Optional[str]:
        return self._backend.jaws_get_version()

    # Scripting
    def jaws_run_script(self, script_name: str) -> bool:
        return self._backend.jaws_run_script(script_name)

    def jaws_run_function(self, function_call: str) -> bool:
        return self._backend.jaws_run_function(function_call)

    def jaws_get_user_settings_directory(self) -> Optional[str]:
        return self._backend.jaws_get_user_settings_directory()

    jfw_run_script = jaws_run_script
    jfw_run_function = jaws_run_function
    jfw_get_user_settings_directory = jaws_get_user_settings_directory

    # Diagnostics
    def get_diagnostics(self) -> Dict[str, Any]:
        return self._backend.get_diagnostics()

    def diagnostics_summary(self) -> str:
        return self._backend.diagnostics_summary()


__all__ = ["UniversalSpeech"]
