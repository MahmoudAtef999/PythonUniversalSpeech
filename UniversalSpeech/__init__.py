"""
This is a Python library for interacting with the UniversalSpeech DLL, providing functionality for speech synthesis and braille display. 
This library works with python 32 and 64 bit.
This module encapsulates the underlying functionality and exposes a simplified interface for working with the UniversalSpeech API.
"""
import ctypes
from typing import Optional, Dict, Any, Union
from .load import Loader
from .exceptions import UnsupportedError

__version__ = "1.0.2.1"

# Identifiers for parameters
VOLUME, VOLUME_MAX, VOLUME_MIN, VOLUME_SUPPORTED, \
RATE, RATE_MAX, RATE_MIN, RATE_SUPPORTED, \
PITCH, PITCH_MAX, PITCH_MIN, PITCH_SUPPORTED, \
INFLECTION, INFLECTION_MAX, INFLECTION_MIN, INFLECTION_SUPPORTED, \
PAUSED, PAUSE_SUPPORTED, \
BUSY, BUSY_SUPPORTED, \
WAIT, WAIT_SUPPORTED \
	= range(0, 22)

ENABLE_NATIVE_SPEECH = 0xFFFF
VOICE = 0x10000
LANGUAGE = 0x20000
SUBENGINE = 0x30000
ENGINE = 0x40000
ENGINE_AVAILABLE = 0x50000
AUTO_ENGINE = 0xFFFE
USER_PARAM = 0x1000000


class UniversalSpeech:
    """
    This class provides a convenient interface for interacting with the UniversalSpeech.dll library.
    It allows you to perform various speech-related operations such as saying messages, controlling speech parameters, and querying information about available speech engines.

    Attributes:
        __uspeech (ctypes.CDLL): An instance of the UniversalSpeech DLL loaded using ctypes.
    """

    def __init__(self) -> None:
        self.__uspeech = Loader().load()
        # Configure ctypes restypes
        self.__uspeech.speechGetString.restype = ctypes.c_wchar_p

    def say(self, msg: str, interrupt: bool = True):
        """Say the given message using the speech engine.
        Parameters:
        - msg (str): The complete message to be spoken.
        - interrupt (bool): Whether to interrupt the current speech if True (optional, default is True).
        """
        return self.__uspeech.speechSay(msg, interrupt)

    def say_a(self, msg: Union[str, bytes], interrupt: bool = True):
        """Say the first letter/character of the given message using the speech engine."""
        if isinstance(msg, str):
            msg = msg.encode("mbcs", errors="replace")
        return self.__uspeech.speechSayA(msg, interrupt)

    # Backward-compatibility alias
    sayA = say_a

    def braille(self, msg: str):
        """Display the given message in braille."""
        return self.__uspeech.brailleDisplay(msg)

    def speech(self, msg: str) -> None:
        """Perform both speech and braille display for the given message."""
        self.say(msg)
        self.braille(msg)

    def speech_a(self, msg: str) -> None:
        """Perform speech_a and braille display for the given message."""
        self.say_a(msg)
        self.braille(msg)

    def stop(self):
        """Stop the speech."""
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
        return self.get_string(ENGINE + engine_id)

    def set_engine(self, engine: str) -> None:
        """
        Set the speech synthesis engine.

        Parameters:
        - engine (str): The name of the speech synthesis engine to set.

        Raises:
        - TypeError: If engine is not a string.
        - UnsupportedError: If the specified engine is not supported. 
          Use self.get_engines() to get a dictionary of supported engines.
        """
        if not isinstance(engine, str):
            raise TypeError("Engine must be a string.")
        engines = self.get_engines()
        if engine not in engines:
            raise UnsupportedError(f"{engine} is not supported. Use self.get_engines() to know the supported engines.")
        
        self.set_value(ENGINE, engines[engine]["id"])

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
