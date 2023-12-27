"""
This is  a Python library for interacting with the UniversalSpeech DLL, providing functionality for speech synthesis and braille display. 
This library works with python 32 and 64 bit.
This module encapsulates the underlying functionality and exposes a simplified interface for working with the UniversalSpeech API.
"""
import ctypes
from .load import Loader
from .exceptions import UnsupportedError

#Identifiers for parameters
VOLUME, VOLUME_MAX, VOLUME_MIN, VOLUME_SUPPORTED, \
RATE, RATE_MAX, RATE_MIN, RATE_SUPPORTED, \
PITCH, PITCH_MAX, PITCH_MIN, PITCH_SUPPORTED, \
INFLEXION, INFLEXION_MAX, INFLEXION_MIN, INFLEXION_SUPPORTED, \
PAUSED, PAUSE_SUPPORTED, \
BUSY, BUSY_SUPPORTED, \
WAIT, WAIT_SUPPORTED \
	= range(0,22)

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

    def say(self, msg:str, interrupt:bool=True):
        """Say the given message using the speech engine.
        Parameters:
        - msg (str): The complete message to be spoken.
        - interrupt (bool): Whether to interrupt the current speech if True (optional, default is True).
        """
        return self.__uspeech.speechSay(msg, interrupt)

    def say_a(self, msg:str, interrupt:bool=True):
        """Say the first letter of the given message using the speech engine."""
        return self.__uspeech.speechSayA(msg, interrupt)

    def braille(self, msg:str):
        """Display the given message in braille."""
        return self.__uspeech.brailleDisplay(msg)

    def speech(self, msg:str):
        """Perform both speech and braille display for the given message."""
        self.say(msg)
        self.braille(msg)

    def speech_a(self, msg:str):
        """Perform  speech_a and braille display for the given message."""
        self.sayA(msg)
        self.braille(msg)

    def stop(self):
        """Stop the speech."""
        return self.__uspeech.speechStop()

    def get_value(self, what):
        """Get the current value of a specific speech parameter."""
        return self.__uspeech.speechGetValue(what)

    def set_value(self, what, value):
        """Set the value of a specific speech parameter."""
        return self.__uspeech.speechSetValue(what, value)

    def get_string(self, what) -> str:
        """Get a string representation of a specific speech parameter."""
        # Set the return type for the function
        self.__uspeech.speechGetString.restype = ctypes.c_wchar_p
        return self.__uspeech.speechGetString(what)

    def enable_native_speech(self, enabled:bool=True) -> None:
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

    def get_engines(self) -> list:
        """Get a list of available speech engines with their names, availability, and IDs."""
        engines = []
        i = 0
        while True:
            name = self.get_string(ENGINE + i)
            if not  name:
                break
            avail = self.get_value(ENGINE_AVAILABLE + i) != 0
            engines.append({
                "name": name,
                "available": avail,
                "Id": i
            })
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
    def inflexion_supported(self) -> bool:
        return self.get_value(INFLEXION_SUPPORTED) != 0

    def set_rate(self, value: int, min_rate: int = None, max_rate: int = None) -> None:
        """
        Set the speech rate and, optionally, the minimum and maximum rates.

        Parameters:
        - rate (int): The desired speech rate.
        - min_rate (int): The minimum allowed speech rate (optional).
        - max_rate (int): The maximum allowed speech rate (optional).

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

    def set_volume(self, value: int, min_volume: int = None, max_volume: int = None) -> None:
        """
        Set the speech volume and, optionally, the minimum and maximum volume.

        Parameters:
        - value (int): The desired speech volume.
        - min_volume (int): The minimum allowed speech volume (optional).
        - max_volume (int): The maximum allowed speech volume (optional).

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

    def set_pitch(self, value: int, min_pitch: int = None, max_pitch: int = None) -> None:
        """
        Set the speech pitch and, optionally, the minimum and maximum pitch.

        Parameters:
        - value (int): The desired speech pitch.
        - min_pitch (int): The minimum allowed speech pitch (optional).
        - max_pitch (int): The maximum allowed speech pitch (optional).

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

    def set_inflexion(self, value: int, min_inflexion: int = None, max_inflexion: int = None) -> None:
        """
        Set the speech inflexion and, optionally, the minimum and maximum inflexion.

        Parameters:
        - value (int): The desired speech inflexion.
        - min_inflexion (int): The minimum allowed speech inflexion (optional).
        - max_inflexion (int): The maximum allowed speech inflexion (optional).

        Raises:
        - UnsupportedError: If the function is not supported with the current engine.
        """
        
        if not self.inflexion_supported:
            raise UnsupportedError("Set inflexion is not supported with the current engine.")
        
        self.set_value(INFLEXION, value)

        if min_inflexion is not None:
            self.set_value(INFLEXION_MIN, min_inflexion)

        if max_inflexion is not None:
            self.set_value(INFLEXION_MAX, max_inflexion)
