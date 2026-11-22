"""
Core UniversalSpeech class and interface.
"""
import ctypes
from typing import Optional, Dict, Any, Union, List
from .loader import Loader
from .exceptions import EngineError, UnsupportedError, VoiceError
from .voices import Voice
from .screen_readers import ScreenReaderInfo
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
    ENGINE, ENGINE_AVAILABLE,
    AUTO_ENGINE,
    ScreenReaderId,
)


class UniversalSpeech:
    """
    This class provides a convenient interface for interacting with the UniversalSpeech.dll library.
    It allows you to perform various speech-related operations such as saying messages, controlling speech parameters, and querying information about available speech engines.

    Attributes:
        __uspeech (ctypes.CDLL): An instance of the UniversalSpeech DLL loaded using ctypes.
    """

    def __init__(self) -> None:
        self.__uspeech = Loader().load()

    def __enter__(self) -> "UniversalSpeech":
        """Support context manager entry: `with UniversalSpeech() as speech:`."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Support context manager exit by stopping any ongoing speech."""
        self.close()

    def close(self) -> None:
        """Stop speech and clean up resources."""
        self.stop()

    def __repr__(self) -> str:
        return f"<UniversalSpeech engine={self.engine_used!r}, reader={self.current_screen_reader_name!r}>"

    def __str__(self) -> str:
        return f"UniversalSpeech({self.engine_used or 'None'})"

    def say(self, msg: str, interrupt: bool = True) -> int:
        """
        Say the given message using the active speech engine (full Unicode).

        Parameters:
        - msg (str): The complete message to be spoken.
        - interrupt (bool): Whether to interrupt current speech if True (default is True).

        Returns:
        - int: 1 if successful, 0 otherwise.
        """
        return self.__uspeech.speechSay(msg, interrupt)

    def say_a(self, msg: Union[str, bytes], interrupt: bool = True) -> int:
        """
        Speak ANSI string using the legacy speechSayA export.
        
        For complete Unicode support (including non-Latin alphabets and symbols),
        prefer the primary say() method.

        Parameters:
        - msg (Union[str, bytes]): The message to be spoken.
        - interrupt (bool): Whether to interrupt current speech if True (default is True).

        Returns:
        - int: 1 if successful, 0 otherwise.
        """
        if isinstance(msg, str):
            msg = msg.encode("mbcs", errors="replace")
        return self.__uspeech.speechSayA(msg, interrupt)

    # Backward-compatibility alias
    sayA = say_a

    def braille(self, msg: str) -> int:
        """
        Display the given message on a connected braille display.

        Parameters:
        - msg (str): The text message to display.

        Returns:
        - int: 1 if successful, 0 otherwise.
        """
        return self.__uspeech.brailleDisplay(msg)

    def speech(self, msg: str, interrupt: bool = True) -> None:
        """
        Perform both speech and braille display for the given message.

        Parameters:
        - msg (str): The complete message to be spoken and displayed in braille.
        - interrupt (bool): Whether to interrupt current speech if True (default is True).
        """
        self.say(msg, interrupt=interrupt)
        self.braille(msg)

    def speech_a(self, msg: Union[str, bytes], interrupt: bool = True) -> None:
        """
        Perform ANSI speech (speechSayA) and braille display for the given message.

        Parameters:
        - msg (Union[str, bytes]): The message to be spoken and displayed in braille.
        - interrupt (bool): Whether to interrupt current speech if True (default is True).
        """
        self.say_a(msg, interrupt=interrupt)
        braille_msg = msg.decode("mbcs", errors="replace") if isinstance(msg, bytes) else msg
        self.braille(braille_msg)

    def stop(self) -> int:
        """
        Stop ongoing speech synthesis immediately.

        Returns:
        - int: 1 if stopped, 0 otherwise.
        """
        return self.__uspeech.speechStop()

    def get_value(self, what: int) -> int:
        """Get the current value of a specific speech parameter."""
        return self.__uspeech.speechGetValue(what)

    def set_value(self, what: int, value: int) -> int:
        """Set the value of a specific speech parameter."""
        return self.__uspeech.speechSetValue(what, value)

    def get_string(self, what: int) -> Optional[str]:
        """Get a string representation of a specific speech parameter."""
        return self.__uspeech.speechGetString(what)

    def set_string(self, what: int, value: str) -> int:
        """Set a string representation of a specific speech parameter."""
        return self.__uspeech.speechSetString(what, value)

    def enable_native_speech(self, enabled: bool = True) -> None:
        """
        Enable or disable the use of native speech engines.

        This method determines whether to use native speech engines, such as SAPI on Windows,
        that are generally reliable and can be used when no other engines are available. 
        If enabled is set to True, native speech engines are used; if set to False, speech
        is ignored in such cases.
        """
        self.set_value(ENABLE_NATIVE_SPEECH, enabled)

    @property
    def engine_used(self) -> str:
        """Get the name of the currently used speech engine."""
        engine_id = self.get_value(ENGINE)
        return self.get_string(ENGINE + engine_id) or ""

    def set_engine(self, engine: Union[str, int, ScreenReaderId]) -> None:
        """
        Set the speech synthesis engine.

        Parameters:
        - engine (Union[str, int, ScreenReaderId]): The name, integer ID, or ScreenReaderId enum of the engine.

        Raises:
        - TypeError: If engine is not a string, integer, or ScreenReaderId.
        - EngineError: If the specified engine is not supported or not available.
        """
        engines = self.get_engines()

        if isinstance(engine, (int, ScreenReaderId)):
            engine_id = int(engine)
            for details in engines.values():
                if details["id"] == engine_id:
                    self.set_value(ENGINE, engine_id)
                    return
            raise EngineError(f"Engine ID {engine_id} is not supported. Use get_engines() to see supported engines.")

        if isinstance(engine, str):
            engine_clean = engine.strip().lower()
            for name, details in engines.items():
                if name.lower() == engine_clean:
                    self.set_value(ENGINE, details["id"])
                    return
            raise EngineError(f"Engine '{engine}' is not supported. Use get_engines() to see supported engines.")

        raise TypeError(f"Engine must be a string, integer, or ScreenReaderId, not {type(engine).__name__}.")

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
        """Get a Dictionary of available speech engines with their names, availability, and IDs."""
        engines = {}
        i = 0
        while True:
            name = self.get_string(ENGINE + i)
            if not name:
                break
            avail = self.get_value(ENGINE_AVAILABLE + i) != 0
            engines[name] = {
                "name": name,
                "available": avail,
                "id": i
            }
            i += 1

        return engines

    def reset_engine(self) -> None:
        """Restore default automatic speech engine selection."""
        self.set_value(ENGINE, -1)

    def say_ssml(self, ssml: str) -> bool:
        """
        Speak text formatted with Speech Synthesis Markup Language (SSML).

        Parameters:
            ssml (str): SSML formatted markup text.

        Returns:
            bool: True if speech was queued/spoken, False otherwise.
        """
        if hasattr(self.__uspeech, "sapiSaySSMLW") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiSaySSMLW(ssml))
        return bool(self.say(ssml))

    @property
    def is_busy(self) -> bool:
        """Check if speech synthesis is currently active / speaking."""
        if self.get_value(BUSY_SUPPORTED) != 0:
            return self.get_value(BUSY) != 0
        if hasattr(self.__uspeech, "sapiIsSpeaking") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiIsSpeaking())
        return False

    @property
    def busy_supported(self) -> bool:
        """Check if querying busy status is supported by the current engine."""
        return self.get_value(BUSY_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiIsSpeaking") and self.engine_used.upper().startswith("SAPI")
        )

    @property
    def is_paused(self) -> bool:
        """Check if speech synthesis is currently paused."""
        if self.get_value(PAUSE_SUPPORTED) != 0:
            return self.get_value(PAUSED) != 0
        if hasattr(self.__uspeech, "sapiIsPaused") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiIsPaused())
        return False

    @property
    def pause_supported(self) -> bool:
        """Check if pausing speech is supported by the current engine."""
        return self.get_value(PAUSE_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiSetPaused") and self.engine_used.upper().startswith("SAPI")
        )

    def pause(self, paused: bool = True) -> None:
        """
        Pause or unpause speech playback.

        Parameters:
            paused (bool): True to pause speech, False to unpause/resume.

        Raises:
            UnsupportedError: If pausing is not supported by the current engine.
        """
        if not self.pause_supported:
            raise UnsupportedError("Pausing is not supported with the current engine.")
        if self.get_value(PAUSE_SUPPORTED) != 0:
            self.set_value(PAUSED, 1 if paused else 0)
        elif hasattr(self.__uspeech, "sapiSetPaused"):
            self.__uspeech.sapiSetPaused(1 if paused else 0)

    def resume(self) -> None:
        """Resume speech playback if currently paused."""
        self.pause(False)

    @property
    def wait_supported(self) -> bool:
        """Check if waiting for speech completion is supported by the current engine."""
        return self.get_value(WAIT_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiWait") and self.engine_used.upper().startswith("SAPI")
        )

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        """
        Wait for speech playback to finish.

        Parameters:
            timeout_ms (Optional[int]): Maximum milliseconds to wait. If None, waits indefinitely.

        Returns:
            bool: True once finished or if supported.
        """
        if timeout_ms is not None:
            return bool(self.set_value(WAIT, timeout_ms))
        if self.get_value(WAIT_SUPPORTED) != 0:
            return bool(self.get_value(WAIT))
        if hasattr(self.__uspeech, "sapiWait") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiWait())
        return True

    @property
    def voice_supported(self) -> bool:
        """Check if changing voices is supported by the current speech engine."""
        return bool(self.get_string(VOICE))

    def get_voices(self) -> List[Voice]:
        """
        Get a list of available voices for the current speech engine.

        Returns:
            List[Voice]: A list of Voice objects available in the current engine.
        """
        voices: List[Voice] = []
        i = 0
        while True:
            name = self.get_string(VOICE + i)
            if not name:
                break
            voices.append(Voice(id=i, name=name))
            i += 1
        return voices

    def get_voice(self) -> Optional[Voice]:
        """
        Get the currently selected voice.

        Returns:
            Optional[Voice]: The current Voice object, or None if no voice is selected.
        """
        current_id = self.get_value(VOICE)
        if current_id < 0:
            if self.voice_supported:
                default_name = self.get_string(VOICE)
                if default_name:
                    return Voice(id=0, name=default_name)
            return None
        name = self.get_string(VOICE + current_id)
        if not name:
            return None
        return Voice(id=current_id, name=name)

    @property
    def current_voice(self) -> Optional[Voice]:
        """Property returning the currently selected voice."""
        return self.get_voice()

    def set_voice(self, voice: Union[int, str, Voice]) -> None:
        """
        Set the current speech synthesis voice.

        Parameters:
            voice (Union[int, str, Voice]): The voice ID (int), name (str), or Voice object.

        Raises:
            VoiceError: If the voice is not found or voices are unsupported.
            TypeError: If voice is of invalid type.
        """
        if not self.voice_supported:
            raise VoiceError("Voices are not supported by the current engine.")

        if isinstance(voice, Voice):
            self.set_value(VOICE, voice.id)
            return

        if isinstance(voice, int):
            name = self.get_string(VOICE + voice)
            if not name:
                raise VoiceError(f"Voice with ID {voice} not found.")
            self.set_value(VOICE, voice)
            return

        if isinstance(voice, str):
            voices = self.get_voices()
            target = voice.strip().lower()
            # 1. Exact match (case-insensitive)
            for v in voices:
                if v.name.lower() == target:
                    self.set_value(VOICE, v.id)
                    return
            # 2. Substring match (case-insensitive)
            matches = [v for v in voices if target in v.name.lower()]
            if matches:
                self.set_value(VOICE, matches[0].id)
                return
            raise VoiceError(f"Voice '{voice}' not found.")

        raise TypeError("Voice must be an int, str, or Voice instance.")

    @property
    def rate_supported(self) -> bool:
        return self.get_value(RATE_SUPPORTED) != 0

    @property
    def volume_supported(self) -> bool:
        return self.get_value(VOLUME_SUPPORTED) != 0

    @property
    def pitch_supported(self) -> bool:
        return self.get_value(PITCH_SUPPORTED) != 0

    @property
    def inflection_supported(self) -> bool:
        return self.get_value(INFLECTION_SUPPORTED) != 0

    def get_rate(self) -> int:
        """Get the current speech rate."""
        if not self.rate_supported:
            raise UnsupportedError("Rate query is not supported with the current engine.")
        return self.get_value(RATE)

    def set_rate(self, value: int, min_rate: Optional[int] = None, max_rate: Optional[int] = None) -> None:
        """
        Set the speech rate and, optionally, the minimum and maximum rates.

        Parameters:
        - value (int): The desired speech rate.
        - min_rate (Optional[int]): The minimum allowed speech rate (optional).
        - max_rate (Optional[int]): The maximum allowed speech rate (optional).

        Raises:
        - UnsupportedError: If the function is not supported with the current engine.
        """
        if not self.rate_supported:
            raise UnsupportedError("Set rate is not supported with the current engine.")
        
        self.set_value(RATE, value)

        if min_rate is not None:
            self.set_value(RATE_MIN, min_rate)

        if max_rate is not None:
            self.set_value(RATE_MAX, max_rate)

    @property
    def rate(self) -> int:
        """Current speech rate."""
        return self.get_rate()

    @rate.setter
    def rate(self, value: int) -> None:
        self.set_rate(value)

    @property
    def rate_min(self) -> int:
        """Minimum speech rate for the current engine."""
        return self.get_value(RATE_MIN)

    @property
    def rate_max(self) -> int:
        """Maximum speech rate for the current engine."""
        return self.get_value(RATE_MAX)

    def get_volume(self) -> int:
        """Get the current speech volume."""
        if not self.volume_supported:
            raise UnsupportedError("Volume query is not supported with the current engine.")
        return self.get_value(VOLUME)

    def set_volume(self, value: int, min_volume: Optional[int] = None, max_volume: Optional[int] = None) -> None:
        """
        Set the speech volume and, optionally, the minimum and maximum volume.

        Parameters:
        - value (int): The desired speech volume.
        - min_volume (Optional[int]): The minimum allowed speech volume (optional).
        - max_volume (Optional[int]): The maximum allowed speech volume (optional).

        Raises:
        - UnsupportedError: If the function is not supported with the current engine.
        """
        if not self.volume_supported:
            raise UnsupportedError("Set volume is not supported with the current engine.")
        
        self.set_value(VOLUME, value)

        if min_volume is not None:
            self.set_value(VOLUME_MIN, min_volume)

        if max_volume is not None:
            self.set_value(VOLUME_MAX, max_volume)

    @property
    def volume(self) -> int:
        """Current speech volume."""
        return self.get_volume()

    @volume.setter
    def volume(self, value: int) -> None:
        self.set_volume(value)

    @property
    def volume_min(self) -> int:
        """Minimum speech volume for the current engine."""
        return self.get_value(VOLUME_MIN)

    @property
    def volume_max(self) -> int:
        """Maximum speech volume for the current engine."""
        return self.get_value(VOLUME_MAX)

    def get_pitch(self) -> int:
        """Get the current speech pitch."""
        if not self.pitch_supported:
            raise UnsupportedError("Pitch query is not supported with the current engine.")
        return self.get_value(PITCH)

    def set_pitch(self, value: int, min_pitch: Optional[int] = None, max_pitch: Optional[int] = None) -> None:
        """
        Set the speech pitch and, optionally, the minimum and maximum pitch.

        Parameters:
        - value (int): The desired speech pitch.
        - min_pitch (Optional[int]): The minimum allowed speech pitch (optional).
        - max_pitch (Optional[int]): The maximum allowed speech pitch (optional).

        Raises:
        - UnsupportedError: If the function is not supported with the current engine.
        """
        if not self.pitch_supported:
            raise UnsupportedError("Set pitch is not supported with the current engine.")
        
        self.set_value(PITCH, value)

        if min_pitch is not None:
            self.set_value(PITCH_MIN, min_pitch)

        if max_pitch is not None:
            self.set_value(PITCH_MAX, max_pitch)

    @property
    def pitch(self) -> int:
        """Current speech pitch."""
        return self.get_pitch()

    @pitch.setter
    def pitch(self, value: int) -> None:
        self.set_pitch(value)

    @property
    def pitch_min(self) -> int:
        """Minimum speech pitch for the current engine."""
        return self.get_value(PITCH_MIN)

    @property
    def pitch_max(self) -> int:
        """Maximum speech pitch for the current engine."""
        return self.get_value(PITCH_MAX)

    def get_inflection(self) -> int:
        """Get the current speech inflection."""
        if not self.inflection_supported:
            raise UnsupportedError("Inflection query is not supported with the current engine.")
        return self.get_value(INFLECTION)

    def set_inflection(self, value: int, min_inflection: Optional[int] = None, max_inflection: Optional[int] = None) -> None:
        """
        Set the speech inflection and, optionally, the minimum and maximum inflection.

        Parameters:
        - value (int): The desired speech inflection.
        - min_inflection (Optional[int]): The minimum allowed speech inflection (optional).
        - max_inflection (Optional[int]): The maximum allowed speech inflection (optional).

        Raises:
        - UnsupportedError: If the function is not supported with the current engine.
        """
        if not self.inflection_supported:
            raise UnsupportedError("Set inflection is not supported with the current engine.")
        
        self.set_value(INFLECTION, value)

        if min_inflection is not None:
            self.set_value(INFLECTION_MIN, min_inflection)

        if max_inflection is not None:
            self.set_value(INFLECTION_MAX, max_inflection)

    @property
    def inflection(self) -> int:
        """Current speech inflection."""
        return self.get_inflection()

    @inflection.setter
    def inflection(self, value: int) -> None:
        self.set_inflection(value)

    @property
    def inflection_min(self) -> int:
        """Minimum speech inflection for the current engine."""
        return self.get_value(INFLECTION_MIN)

    @property
    def inflection_max(self) -> int:
        """Maximum speech inflection for the current engine."""
        return self.get_value(INFLECTION_MAX)

    # -------------------------------------------------------------------------
    # Screen Reader Information & Direct Checks
    # -------------------------------------------------------------------------

    @property
    def current_screen_reader_name(self) -> str:
        """Get the name of the currently active screen reader (e.g., 'NVDA', 'Jaws', 'SAPI5')."""
        if hasattr(self.__uspeech, "getCurrentScreenReaderNameW"):
            name = self.__uspeech.getCurrentScreenReaderNameW()
            if name:
                return name
        return ""

    @property
    def current_screen_reader_id(self) -> int:
        """Get the ID of the currently active screen reader."""
        if hasattr(self.__uspeech, "getCurrentScreenReader"):
            return self.__uspeech.getCurrentScreenReader()
        return -1

    def get_supported_screen_readers(self) -> List[str]:
        """Get a list of all screen readers supported by UniversalSpeech.dll."""
        readers: List[str] = []
        if hasattr(self.__uspeech, "getSupportedScreenReadersCount") and hasattr(self.__uspeech, "getScreenReaderNameW"):
            count = self.__uspeech.getSupportedScreenReadersCount()
            for i in range(count):
                name = self.__uspeech.getScreenReaderNameW(i)
                if name:
                    readers.append(name)
        return readers

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        """
        Get detailed information (id, name, availability) for all supported screen readers.

        Returns:
            List[ScreenReaderInfo]: A list of ScreenReaderInfo objects.
        """
        info_list: List[ScreenReaderInfo] = []
        names = self.get_supported_screen_readers()
        for idx, name in enumerate(names):
            # Check availability using specific DLL functions or engine check
            available = self._is_reader_available(idx, name)
            info_list.append(ScreenReaderInfo(id=idx, name=name, available=available))
        return info_list

    def _is_reader_available(self, reader_id: int, name: str) -> bool:
        """Helper to determine availability for a given screen reader."""
        norm_name = name.lower()
        if "nvda" in norm_name:
            return self.nvda_is_available()
        elif "jaws" in norm_name or "jfw" in norm_name:
            return self.jaws_is_available()
        elif "sapi" in norm_name:
            return self.sapi_is_available()
        elif "system access" in norm_name:
            return self.system_access_is_available()
        elif "supernova" in norm_name:
            return self.supernova_is_available()
        elif "window" in norm_name and "eye" in norm_name:
            return self.window_eyes_is_available()
        elif "cobra" in norm_name:
            return self.cobra_is_available()
        elif "zoomtext" in norm_name:
            return self.zoomtext_is_available()
        elif "narrator" in norm_name:
            return self.narrator_is_available()
        elif "zdsr" in norm_name:
            return self.zdsr_is_available()
        return False

    def nvda_is_available(self) -> bool:
        """Check if NVDA is running and available."""
        if hasattr(self.__uspeech, "nvdaIsAvailable"):
            return bool(self.__uspeech.nvdaIsAvailable())
        return False

    def jaws_is_available(self) -> bool:
        """Check if JAWS is running and available."""
        if hasattr(self.__uspeech, "jfwIsAvailable"):
            return bool(self.__uspeech.jfwIsAvailable())
        return False

    def sapi_is_available(self) -> bool:
        """Check if SAPI5 speech synthesis is available on the system."""
        if hasattr(self.__uspeech, "sapiIsAvailable"):
            return bool(self.__uspeech.sapiIsAvailable())
        return False

    def system_access_is_available(self) -> bool:
        """Check if System Access is running and available."""
        if hasattr(self.__uspeech, "saIsAvailable"):
            return bool(self.__uspeech.saIsAvailable())
        return False

    def supernova_is_available(self) -> bool:
        """Check if Dolphin Supernova is running and available."""
        if hasattr(self.__uspeech, "dolIsAvailable"):
            return bool(self.__uspeech.dolIsAvailable())
        return False

    def window_eyes_is_available(self) -> bool:
        """Check if Window-Eyes is running and available."""
        if hasattr(self.__uspeech, "weIsAvailable"):
            return bool(self.__uspeech.weIsAvailable())
        return False

    def cobra_is_available(self) -> bool:
        """Check if Cobra screen reader is running and available."""
        if hasattr(self.__uspeech, "cbrIsAvailable"):
            return bool(self.__uspeech.cbrIsAvailable())
        return False

    def zoomtext_is_available(self) -> bool:
        """Check if ZoomText is running and available."""
        if hasattr(self.__uspeech, "ztIsAvailable"):
            return bool(self.__uspeech.ztIsAvailable())
        return False

    def narrator_is_available(self) -> bool:
        """Check if Windows Narrator is running and available."""
        if hasattr(self.__uspeech, "narIsAvailable"):
            return bool(self.__uspeech.narIsAvailable())
        return False

    def zdsr_is_available(self) -> bool:
        """Check if ZDSR screen reader is running and available."""
        if hasattr(self.__uspeech, "zdsrIsAvailable"):
            return bool(self.__uspeech.zdsrIsAvailable())
        return False

    def nvda_get_version(self) -> Optional[str]:
        """
        Get the version string of the currently running NVDA screen reader.

        Returns:
            Optional[str]: The NVDA version string (e.g. '2026.2'), or None if NVDA is not running.
        """
        if hasattr(self.__uspeech, "nvdaGetRunningVersion"):
            buf = ctypes.create_string_buffer(256)
            if self.__uspeech.nvdaGetRunningVersion(buf, 256):
                val = buf.value.decode("utf-8", errors="replace").strip()
                if val:
                    return val
        return None

    def jfw_get_version(self) -> Optional[str]:
        """
        Get the version string of the currently running JAWS screen reader.

        Returns:
            Optional[str]: The JAWS version string (e.g. '2025.0'), or None if JAWS is not running.
        """
        if hasattr(self.__uspeech, "jfwGetRunningVersion"):
            buf = ctypes.create_string_buffer(256)
            if self.__uspeech.jfwGetRunningVersion(buf, 256):
                val = buf.value.decode("utf-8", errors="replace").strip()
                if val:
                    return val
        return None


__all__ = ["UniversalSpeech"]
