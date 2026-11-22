"""
Abstract base backend defining the contract and default behaviors for platform-specific speech engines.
"""
from abc import ABC, abstractmethod
import re
from typing import Optional, Dict, Any, Union, List, Tuple
from ..voices import Voice
from ..screen_readers import ScreenReaderInfo
from ..constants import ScreenReaderId
from ..exceptions import UnsupportedError


class BaseBackend(ABC):
    """Abstract base class that all platform speech backends implement."""

    @abstractmethod
    def say(self, msg: str, interrupt: bool = True) -> int:
        """Speak the given message."""
        pass

    def say_a(self, msg: Union[str, bytes], interrupt: bool = True) -> int:
        """Speak ANSI / byte string."""
        if isinstance(msg, bytes):
            msg = msg.decode("utf-8", errors="replace")
        return self.say(msg, interrupt=interrupt)

    # Legacy alias
    sayA = say_a

    def braille(self, msg: str) -> int:
        """Display message on connected braille display (if supported)."""
        return 0

    def speech(self, msg: str, interrupt: bool = True) -> None:
        """Perform both speech and braille display."""
        self.say(msg, interrupt=interrupt)
        self.braille(msg)

    def speech_a(self, msg: Union[str, bytes], interrupt: bool = True) -> None:
        """Perform ANSI speech and braille display."""
        self.say_a(msg, interrupt=interrupt)
        braille_msg = msg.decode("utf-8", errors="replace") if isinstance(msg, bytes) else msg
        self.braille(braille_msg)

    @abstractmethod
    def stop(self) -> int:
        """Stop current speech output."""
        pass

    def close(self) -> None:
        """Clean up backend resources."""
        self.stop()

    def get_value(self, what: int) -> int:
        """Get integer parameter value."""
        raise UnsupportedError(f"get_value({what}) is not supported on {self.__class__.__name__}")

    def set_value(self, what: int, value: int) -> int:
        """Set integer parameter value."""
        raise UnsupportedError(f"set_value({what}) is not supported on {self.__class__.__name__}")

    def get_string(self, what: int) -> Optional[str]:
        """Get string parameter value."""
        raise UnsupportedError(f"get_string({what}) is not supported on {self.__class__.__name__}")

    def set_string(self, what: int, value: str) -> int:
        """Set string parameter value."""
        raise UnsupportedError(f"set_string({what}) is not supported on {self.__class__.__name__}")

    def enable_native_speech(self, enabled: bool = True) -> None:
        """Enable or disable native speech fallback."""
        pass

    @property
    @abstractmethod
    def engine_used(self) -> str:
        """Name of the currently used speech engine."""
        pass

    def set_engine(self, engine: Union[str, int, ScreenReaderId, ScreenReaderInfo]) -> None:
        """Set active speech engine."""
        pass

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
        """Get dictionary of all engines."""
        return {}

    def reset_engine(self) -> None:
        """Restore automatic engine selection."""
        pass

    def say_ssml(self, ssml: str) -> bool:
        """Speak SSML / markup text (default strips tags and speaks plain text)."""
        plain = re.sub(r"<[^>]+>", "", ssml)
        return bool(self.say(plain))

    @property
    def is_busy(self) -> bool:
        """True if speech is currently outputting."""
        return False

    @property
    def busy_supported(self) -> bool:
        """True if busy querying is supported."""
        return False

    @property
    def is_paused(self) -> bool:
        """True if speech is paused."""
        return False

    @property
    def pause_supported(self) -> bool:
        """True if pause/resume is supported."""
        return False

    def pause(self, paused: bool = True) -> None:
        """Pause or unpause speech playback."""
        pass

    def resume(self) -> None:
        """Resume speech playback."""
        self.pause(False)

    @property
    def wait_supported(self) -> bool:
        """True if wait synchronization is supported."""
        return False

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        """Wait for speech playback to finish."""
        return True

    @property
    def voice_supported(self) -> bool:
        """True if changing voices is supported."""
        return False

    def get_voice(self) -> Optional[Voice]:
        """Get currently active voice."""
        return None

    def set_voice(self, voice: Union[Voice, int, str]) -> None:
        """Set active voice."""
        raise UnsupportedError(f"Voices are not supported on {self.__class__.__name__}")

    @property
    def current_voice(self) -> Optional[Voice]:
        """Currently active Voice object."""
        return self.get_voice()

    @current_voice.setter
    def current_voice(self, voice: Union[Voice, int, str]) -> None:
        self.set_voice(voice)

    def get_voices(self) -> List[Voice]:
        """Get list of available voices."""
        return []

    # Rate
    @property
    def rate_supported(self) -> bool:
        """True if rate adjustment is supported."""
        return False

    def get_rate(self) -> int:
        """Get current speech rate."""
        return 50

    def set_rate(self, rate: int) -> None:
        """Set speech rate."""
        pass

    @property
    def rate(self) -> int:
        """Speech rate property."""
        return self.get_rate()

    @rate.setter
    def rate(self, value: int) -> None:
        self.set_rate(value)

    @property
    def rate_min(self) -> int:
        """Minimum speech rate."""
        return 0

    @property
    def rate_max(self) -> int:
        """Maximum speech rate."""
        return 100

    @property
    def rate_range(self) -> Tuple[int, int]:
        """Speech rate range (min, max)."""
        return (self.rate_min, self.rate_max)

    # Volume
    @property
    def volume_supported(self) -> bool:
        """True if volume adjustment is supported."""
        return False

    def get_volume(self) -> int:
        """Get current speech volume."""
        return 100

    def set_volume(self, volume: int) -> None:
        """Set speech volume."""
        pass

    @property
    def volume(self) -> int:
        """Speech volume property."""
        return self.get_volume()

    @volume.setter
    def volume(self, value: int) -> None:
        self.set_volume(value)

    @property
    def volume_min(self) -> int:
        """Minimum speech volume."""
        return 0

    @property
    def volume_max(self) -> int:
        """Maximum speech volume."""
        return 100

    @property
    def volume_range(self) -> Tuple[int, int]:
        """Speech volume range (min, max)."""
        return (self.volume_min, self.volume_max)

    # Pitch
    @property
    def pitch_supported(self) -> bool:
        """True if pitch adjustment is supported."""
        return False

    def get_pitch(self) -> int:
        """Get current pitch."""
        return 50

    def set_pitch(self, pitch: int) -> None:
        """Set pitch."""
        pass

    @property
    def pitch(self) -> int:
        """Speech pitch property."""
        return self.get_pitch()

    @pitch.setter
    def pitch(self, value: int) -> None:
        self.set_pitch(value)

    @property
    def pitch_min(self) -> int:
        """Minimum pitch."""
        return 0

    @property
    def pitch_max(self) -> int:
        """Maximum pitch."""
        return 100

    @property
    def pitch_range(self) -> Tuple[int, int]:
        """Speech pitch range (min, max)."""
        return (self.pitch_min, self.pitch_max)

    # Inflection
    @property
    def inflection_supported(self) -> bool:
        """True if inflection adjustment is supported."""
        return False

    def get_inflection(self) -> int:
        """Get current inflection."""
        return 50

    def set_inflection(self, inflection: int) -> None:
        """Set inflection."""
        pass

    @property
    def inflection(self) -> int:
        """Speech inflection property."""
        return self.get_inflection()

    @inflection.setter
    def inflection(self, value: int) -> None:
        self.set_inflection(value)

    @property
    def inflection_min(self) -> int:
        """Minimum inflection."""
        return 0

    @property
    def inflection_max(self) -> int:
        """Maximum inflection."""
        return 100

    @property
    def inflection_range(self) -> Tuple[int, int]:
        """Speech inflection range (min, max)."""
        return (self.inflection_min, self.inflection_max)

    # Screen Readers & Engines
    @property
    def current_screen_reader_name(self) -> str:
        """Name of the active screen reader."""
        return ""

    @property
    def current_screen_reader_id(self) -> int:
        """ID of the active screen reader."""
        return 0

    def get_supported_screen_readers(self) -> List[str]:
        """List names of supported screen readers."""
        return []

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        """List all screen reader objects."""
        return []

    def _is_reader_available(self, reader_id: int, name: str) -> bool:
        """Check if screen reader is available."""
        return False

    # Screen reader checks (Windows defaults to False)
    def nvda_is_available(self) -> bool:
        return False

    def jaws_is_available(self) -> bool:
        return False

    def sapi_is_available(self) -> bool:
        return False

    def system_access_is_available(self) -> bool:
        return False

    def supernova_is_available(self) -> bool:
        return False

    def window_eyes_is_available(self) -> bool:
        return False

    def cobra_is_available(self) -> bool:
        return False

    def zoomtext_is_available(self) -> bool:
        return False

    def narrator_is_available(self) -> bool:
        return False

    def zdsr_is_available(self) -> bool:
        return False

    # Versions
    def nvda_get_version(self) -> Optional[str]:
        return None

    def jfw_get_version(self) -> Optional[str]:
        return None

    def jaws_get_version(self) -> Optional[str]:
        return self.jfw_get_version()

    # Scripting
    def jaws_run_script(self, script_name: str) -> bool:
        return False

    def jaws_run_function(self, function_call: str) -> bool:
        return False

    def jaws_get_user_settings_directory(self) -> Optional[str]:
        return None

    jfw_run_script = jaws_run_script
    jfw_run_function = jaws_run_function
    jfw_get_user_settings_directory = jaws_get_user_settings_directory

    # Diagnostics
    @abstractmethod
    def get_diagnostics(self) -> Dict[str, Any]:
        """Gather diagnostics about backend, engines, parameters, and environment."""
        pass

    def diagnostics_summary(self) -> str:
        """Format diagnostic information as a human-readable text report."""
        diag = self.get_diagnostics()
        lines = [
            "==================================================",
            "        UniversalSpeech Diagnostics Report        ",
            "==================================================",
            f"Platform:             {diag.get('platform', 'Unknown')}",
            f"Backend:              {self.__class__.__name__}",
            f"Active Engine:        {diag.get('engine_used') or 'None'}",
            f"Active Screen Reader: {diag.get('active_screen_reader_name') or 'None'} (ID: {diag.get('active_screen_reader_id', 0)})",
            "",
            "--- Capabilities & Parameters ---",
        ]
        caps = diag.get("capabilities", {})
        params = diag.get("parameters", {})
        lines.append(f"  Rate:       {'Supported' if caps.get('rate') else 'Unsupported'}" + (f" (Current: {params.get('rate')}, Range: {params.get('rate_range')})" if caps.get('rate') else ""))
        lines.append(f"  Volume:     {'Supported' if caps.get('volume') else 'Unsupported'}" + (f" (Current: {params.get('volume')}, Range: {params.get('volume_range')})" if caps.get('volume') else ""))
        lines.append(f"  Pitch:      {'Supported' if caps.get('pitch') else 'Unsupported'}" + (f" (Current: {params.get('pitch')}, Range: {params.get('pitch_range')})" if caps.get('pitch') else ""))
        lines.append(f"  Inflection: {'Supported' if caps.get('inflection') else 'Unsupported'}" + (f" (Current: {params.get('inflection')}, Range: {params.get('inflection_range')})" if caps.get('inflection') else ""))
        lines.append("==================================================")
        return "\n".join(lines)
