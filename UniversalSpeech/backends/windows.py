"""
Windows backend for UniversalSpeech, interfacing with UniversalSpeech.dll.
"""
import sys
import time
import ctypes
import warnings
from typing import Optional, Dict, Any, Union, List, Tuple
from .base import BaseBackend
from ..loader import Loader
from ..exceptions import EngineError, UnsupportedError, VoiceError
from ..voices import Voice
from ..screen_readers import ScreenReaderInfo
from ..constants import (
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


class WindowsBackend(BaseBackend):
    """
    Windows-specific backend wrapping UniversalSpeech.dll via ctypes.
    """

    def __init__(self) -> None:
        self.__uspeech = Loader().load()

    @property
    def uspeech(self) -> ctypes.CDLL:
        """Underlying ctypes.CDLL object."""
        return self.__uspeech

    def say(self, msg: str, interrupt: bool = True) -> int:
        return int(self.__uspeech.speechSay(msg, interrupt))

    def say_a(self, msg: Union[str, bytes], interrupt: bool = True) -> int:
        if isinstance(msg, str):
            msg = msg.encode("mbcs", errors="replace")
        return int(self.__uspeech.speechSayA(msg, interrupt))

    def braille(self, msg: str) -> int:
        return int(self.__uspeech.brailleDisplay(msg))

    def speech(self, msg: str, interrupt: bool = True) -> None:
        self.say(msg, interrupt=interrupt)
        self.braille(msg)

    def speech_a(self, msg: Union[str, bytes], interrupt: bool = True) -> None:
        self.say_a(msg, interrupt=interrupt)
        braille_msg = msg.decode("mbcs", errors="replace") if isinstance(msg, bytes) else msg
        self.braille(braille_msg)

    def stop(self) -> int:
        return int(self.__uspeech.speechStop())

    def close(self) -> None:
        pass

    def get_value(self, what: int) -> int:
        return int(self.__uspeech.speechGetValue(what))

    def set_value(self, what: int, value: int) -> int:
        return int(self.__uspeech.speechSetValue(what, value))

    def get_string(self, what: int) -> Optional[str]:
        res = self.__uspeech.speechGetString(what)
        return str(res) if res is not None else None

    def set_string(self, what: int, value: str) -> int:
        return int(self.__uspeech.speechSetString(what, value))

    def enable_native_speech(self, enabled: bool = True) -> None:
        self.set_value(ENABLE_NATIVE_SPEECH, enabled)

    @property
    def engine_used(self) -> str:
        engine_id = self.get_value(ENGINE)
        return self.get_string(ENGINE + engine_id) or ""

    def set_engine(self, engine: Union[str, int, ScreenReaderId, ScreenReaderInfo]) -> None:
        if isinstance(engine, ScreenReaderInfo):
            engine = engine.id

        if isinstance(engine, (int, ScreenReaderId)):
            engine_id = int(engine)
            if engine_id in (-1, AUTO_ENGINE):
                self.reset_engine()
                return
            engines = self.get_engines()
            for details in engines.values():
                if details["id"] == engine_id:
                    self.set_value(ENGINE, engine_id)
                    return
            raise EngineError(
                f"Engine ID {engine_id} is not supported. Available engines: {list(engines.keys())}"
            )

        if isinstance(engine, str):
            clean = engine.strip().lower()
            if clean in ("auto", "default", "automatic"):
                self.reset_engine()
                return
            clean_norm = "".join(c for c in clean if c.isalnum())
            engines = self.get_engines()
            for name, details in engines.items():
                name_clean = name.lower()
                name_norm = "".join(c for c in name_clean if c.isalnum())
                if name_clean == clean or name_norm == clean_norm:
                    self.set_value(ENGINE, details["id"])
                    return
            raise EngineError(
                f"Engine '{engine}' is not supported. Available engines: {list(engines.keys())}"
            )

        raise TypeError(
            f"Engine must be a string, integer, ScreenReaderId, or ScreenReaderInfo, not {type(engine).__name__}."
        )

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
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
        self.set_value(ENGINE, -1)

    def say_ssml(self, ssml: str) -> bool:
        if hasattr(self.__uspeech, "sapiSaySSMLW") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiSaySSMLW(ssml))
        return bool(self.say(ssml))

    @property
    def is_busy(self) -> bool:
        if self.get_value(BUSY_SUPPORTED) != 0:
            return self.get_value(BUSY) != 0
        if hasattr(self.__uspeech, "sapiIsSpeaking") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiIsSpeaking())
        return False

    @property
    def busy_supported(self) -> bool:
        return self.get_value(BUSY_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiIsSpeaking") and self.engine_used.upper().startswith("SAPI")
        )

    @property
    def is_paused(self) -> bool:
        if self.get_value(PAUSE_SUPPORTED) != 0:
            return self.get_value(PAUSED) != 0
        if hasattr(self.__uspeech, "sapiIsPaused") and self.engine_used.upper().startswith("SAPI"):
            return bool(self.__uspeech.sapiIsPaused())
        return False

    @property
    def pause_supported(self) -> bool:
        return self.get_value(PAUSE_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiSetPaused") and self.engine_used.upper().startswith("SAPI")
        )

    def pause(self, paused: bool = True) -> None:
        if not self.pause_supported:
            raise UnsupportedError("Pausing is not supported with the current engine.")
        if self.get_value(PAUSE_SUPPORTED) != 0:
            self.set_value(PAUSED, 1 if paused else 0)
        elif hasattr(self.__uspeech, "sapiSetPaused"):
            self.__uspeech.sapiSetPaused(1 if paused else 0)

    def resume(self) -> None:
        self.pause(False)

    @property
    def wait_supported(self) -> bool:
        return self.get_value(WAIT_SUPPORTED) != 0 or (
            hasattr(self.__uspeech, "sapiWait") and self.engine_used.upper().startswith("SAPI")
        )

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        if not self.wait_supported and not self.busy_supported:
            return False

        start_time = time.time()
        timeout_sec = (timeout_ms / 1000.0) if timeout_ms is not None else None

        # Execute native wait if supported by the engine/DLL
        if self.wait_supported:
            if timeout_ms is not None:
                self.set_value(WAIT, timeout_ms)
            else:
                if self.get_value(WAIT_SUPPORTED) != 0:
                    self.get_value(WAIT)
                elif hasattr(self.__uspeech, "sapiWait") and self.engine_used.upper().startswith("SAPI"):
                    self.__uspeech.sapiWait()

        # If busy checking is supported, check or poll until playback finishes or timeout expires
        if self.busy_supported:
            while self.is_busy:
                if timeout_sec is not None and (time.time() - start_time) >= timeout_sec:
                    return False
                time.sleep(0.02)
            return not self.is_busy

        return True

    @property
    def voice_supported(self) -> bool:
        return bool(self.get_string(VOICE))

    def get_voices(self) -> List[Voice]:
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
        return self.get_voice()

    @current_voice.setter
    def current_voice(self, voice: Union[int, str, Voice]) -> None:
        self.set_voice(voice)

    def set_voice(self, voice: Union[int, str, Voice]) -> None:
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
            for v in voices:
                if v.name.lower() == target:
                    self.set_value(VOICE, v.id)
                    return
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
        if not self.rate_supported:
            raise UnsupportedError("Rate query is not supported with the current engine.")
        return self.get_value(RATE)

    def set_rate(self, value: int, min_rate: Optional[int] = None, max_rate: Optional[int] = None) -> None:
        if not self.rate_supported:
            raise UnsupportedError("Set rate is not supported with the current engine.")
        if min_rate is not None or max_rate is not None:
            warnings.warn(
                "min_rate and max_rate parameters are deprecated and ignored because engine boundaries are read-only; use rate_range instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.set_value(RATE, value)

    @property
    def rate(self) -> int:
        return self.get_rate()

    @rate.setter
    def rate(self, value: int) -> None:
        self.set_rate(value)

    @property
    def rate_min(self) -> int:
        return self.get_value(RATE_MIN)

    @property
    def rate_max(self) -> int:
        return self.get_value(RATE_MAX)

    @property
    def rate_range(self) -> Tuple[int, int]:
        return (self.rate_min, self.rate_max)

    def get_volume(self) -> int:
        if not self.volume_supported:
            raise UnsupportedError("Volume query is not supported with the current engine.")
        return self.get_value(VOLUME)

    def set_volume(self, value: int, min_volume: Optional[int] = None, max_volume: Optional[int] = None) -> None:
        if not self.volume_supported:
            raise UnsupportedError("Set volume is not supported with the current engine.")
        if min_volume is not None or max_volume is not None:
            warnings.warn(
                "min_volume and max_volume parameters are deprecated and ignored because engine boundaries are read-only; use volume_range instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.set_value(VOLUME, value)

    @property
    def volume(self) -> int:
        return self.get_volume()

    @volume.setter
    def volume(self, value: int) -> None:
        self.set_volume(value)

    @property
    def volume_min(self) -> int:
        return self.get_value(VOLUME_MIN)

    @property
    def volume_max(self) -> int:
        return self.get_value(VOLUME_MAX)

    @property
    def volume_range(self) -> Tuple[int, int]:
        return (self.volume_min, self.volume_max)

    def get_pitch(self) -> int:
        if not self.pitch_supported:
            raise UnsupportedError("Pitch query is not supported with the current engine.")
        return self.get_value(PITCH)

    def set_pitch(self, value: int, min_pitch: Optional[int] = None, max_pitch: Optional[int] = None) -> None:
        if not self.pitch_supported:
            raise UnsupportedError("Set pitch is not supported with the current engine.")
        if min_pitch is not None or max_pitch is not None:
            warnings.warn(
                "min_pitch and max_pitch parameters are deprecated and ignored because engine boundaries are read-only; use pitch_range instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.set_value(PITCH, value)

    @property
    def pitch(self) -> int:
        return self.get_pitch()

    @pitch.setter
    def pitch(self, value: int) -> None:
        self.set_pitch(value)

    @property
    def pitch_min(self) -> int:
        return self.get_value(PITCH_MIN)

    @property
    def pitch_max(self) -> int:
        return self.get_value(PITCH_MAX)

    @property
    def pitch_range(self) -> Tuple[int, int]:
        return (self.pitch_min, self.pitch_max)

    def get_inflection(self) -> int:
        if not self.inflection_supported:
            raise UnsupportedError("Inflection query is not supported with the current engine.")
        return self.get_value(INFLECTION)

    def set_inflection(self, value: int, min_inflection: Optional[int] = None, max_inflection: Optional[int] = None) -> None:
        if not self.inflection_supported:
            raise UnsupportedError("Set inflection is not supported with the current engine.")
        if min_inflection is not None or max_inflection is not None:
            warnings.warn(
                "min_inflection and max_inflection parameters are deprecated and ignored because engine boundaries are read-only; use inflection_range instead.",
                DeprecationWarning,
                stacklevel=2,
            )
        self.set_value(INFLECTION, value)

    @property
    def inflection(self) -> int:
        return self.get_inflection()

    @inflection.setter
    def inflection(self, value: int) -> None:
        self.set_inflection(value)

    @property
    def inflection_min(self) -> int:
        return self.get_value(INFLECTION_MIN)

    @property
    def inflection_max(self) -> int:
        return self.get_value(INFLECTION_MAX)

    @property
    def inflection_range(self) -> Tuple[int, int]:
        return (self.inflection_min, self.inflection_max)

    @property
    def current_screen_reader_name(self) -> str:
        if hasattr(self.__uspeech, "getCurrentScreenReaderNameW"):
            name = self.__uspeech.getCurrentScreenReaderNameW()
            if name:
                return str(name)
        return ""

    @property
    def current_screen_reader_id(self) -> int:
        if hasattr(self.__uspeech, "getCurrentScreenReader"):
            return int(self.__uspeech.getCurrentScreenReader())
        return -1

    def get_supported_screen_readers(self) -> List[str]:
        readers: List[str] = []
        if hasattr(self.__uspeech, "getSupportedScreenReadersCount") and hasattr(self.__uspeech, "getScreenReaderNameW"):
            count = self.__uspeech.getSupportedScreenReadersCount()
            for i in range(count):
                name = self.__uspeech.getScreenReaderNameW(i)
                if name:
                    readers.append(name)
        return readers

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        info_list: List[ScreenReaderInfo] = []
        names = self.get_supported_screen_readers()
        for idx, name in enumerate(names):
            available = self._is_reader_available(idx, name)
            info_list.append(ScreenReaderInfo(id=idx, name=name, available=available))
        return info_list

    def _is_reader_available(self, reader_id: int, name: str) -> bool:
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
        if hasattr(self.__uspeech, "nvdaIsAvailable"):
            return bool(self.__uspeech.nvdaIsAvailable())
        return False

    def jaws_is_available(self) -> bool:
        if hasattr(self.__uspeech, "jfwIsAvailable"):
            return bool(self.__uspeech.jfwIsAvailable())
        return False

    def sapi_is_available(self) -> bool:
        if hasattr(self.__uspeech, "sapiIsAvailable"):
            return bool(self.__uspeech.sapiIsAvailable())
        return False

    def system_access_is_available(self) -> bool:
        if hasattr(self.__uspeech, "saIsAvailable"):
            return bool(self.__uspeech.saIsAvailable())
        return False

    def supernova_is_available(self) -> bool:
        if hasattr(self.__uspeech, "dolIsAvailable"):
            return bool(self.__uspeech.dolIsAvailable())
        return False

    def window_eyes_is_available(self) -> bool:
        if hasattr(self.__uspeech, "weIsAvailable"):
            return bool(self.__uspeech.weIsAvailable())
        return False

    def cobra_is_available(self) -> bool:
        if hasattr(self.__uspeech, "cbrIsAvailable"):
            return bool(self.__uspeech.cbrIsAvailable())
        return False

    def zoomtext_is_available(self) -> bool:
        if hasattr(self.__uspeech, "ztIsAvailable"):
            return bool(self.__uspeech.ztIsAvailable())
        return False

    def narrator_is_available(self) -> bool:
        if hasattr(self.__uspeech, "narIsAvailable"):
            return bool(self.__uspeech.narIsAvailable())
        return False

    def zdsr_is_available(self) -> bool:
        if hasattr(self.__uspeech, "zdsrIsAvailable"):
            return bool(self.__uspeech.zdsrIsAvailable())
        return False

    def nvda_get_version(self) -> Optional[str]:
        if hasattr(self.__uspeech, "nvdaGetRunningVersion"):
            buf = ctypes.create_string_buffer(256)
            if self.__uspeech.nvdaGetRunningVersion(buf, 256):
                val = buf.value.decode("utf-8", errors="replace").strip()
                if val:
                    return val
        return None

    def jfw_get_version(self) -> Optional[str]:
        if hasattr(self.__uspeech, "jfwGetRunningVersion"):
            buf = ctypes.create_string_buffer(256)
            if self.__uspeech.jfwGetRunningVersion(buf, 256):
                val = buf.value.decode("utf-8", errors="replace").strip()
                if val:
                    return val
        return None

    jaws_get_version = jfw_get_version

    def jaws_run_script(self, script_name: str) -> bool:
        if hasattr(self.__uspeech, "jfwRunScriptW"):
            return bool(self.__uspeech.jfwRunScriptW(script_name))
        return False

    jfw_run_script = jaws_run_script

    def jaws_run_function(self, function_call: str) -> bool:
        if hasattr(self.__uspeech, "jfwRunFunctionW"):
            return bool(self.__uspeech.jfwRunFunctionW(function_call))
        return False

    jfw_run_function = jaws_run_function

    def jaws_get_user_settings_directory(self) -> Optional[str]:
        if hasattr(self.__uspeech, "jfwGetUserSettingsDirectory"):
            buf = ctypes.create_string_buffer(512)
            if self.__uspeech.jfwGetUserSettingsDirectory(buf, 512):
                val = buf.value.decode("utf-8", errors="replace").strip()
                if val:
                    return val
        return None

    jfw_get_user_settings_directory = jaws_get_user_settings_directory

    def get_diagnostics(self) -> Dict[str, Any]:
        active_voice = self.get_voice()
        installed_voices = self.get_voices() if self.voice_supported else []
        screen_readers = []
        for r in self.get_screen_readers():
            ver = None
            if "nvda" in r.name.lower():
                ver = self.nvda_get_version()
            elif "jaws" in r.name.lower() or "jfw" in r.name.lower():
                ver = self.jfw_get_version()
            screen_readers.append({
                "id": r.id,
                "name": r.name,
                "available": r.available,
                "version": ver,
            })

        return {
            "platform": sys.platform,
            "engine_used": self.engine_used,
            "active_screen_reader_name": self.current_screen_reader_name or None,
            "active_screen_reader_id": self.current_screen_reader_id,
            "screen_readers": screen_readers,
            "engines": self.get_engines(),
            "capabilities": {
                "rate": self.rate_supported,
                "volume": self.volume_supported,
                "pitch": self.pitch_supported,
                "inflection": self.inflection_supported,
                "pause": self.pause_supported,
                "busy": self.busy_supported,
                "wait": self.wait_supported,
                "voices": self.voice_supported,
            },
            "parameters": {
                "rate": self.get_rate() if self.rate_supported else None,
                "rate_range": self.rate_range if self.rate_supported else None,
                "volume": self.get_volume() if self.volume_supported else None,
                "volume_range": self.volume_range if self.volume_supported else None,
                "pitch": self.get_pitch() if self.pitch_supported else None,
                "pitch_range": self.pitch_range if self.pitch_supported else None,
                "inflection": self.get_inflection() if self.inflection_supported else None,
                "inflection_range": self.inflection_range if self.inflection_supported else None,
                "is_busy": self.is_busy,
                "is_paused": self.is_paused,
            },
            "active_voice": {
                "id": active_voice.id,
                "name": active_voice.name,
            } if active_voice else None,
            "voices_count": len(installed_voices),
        }


__all__ = ["WindowsBackend"]
