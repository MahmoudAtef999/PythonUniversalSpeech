"""
macOS backend for UniversalSpeech supporting Apple VoiceOver and native speech (/usr/bin/say)
with zero external dependencies.
"""
import os
import sys
import shutil
import subprocess
from typing import Optional, Dict, Any, Union, List, Tuple
from .base import BaseBackend
from ..voices import Voice
from ..screen_readers import ScreenReaderInfo
from ..constants import ScreenReaderId
from ..exceptions import UnsupportedError, EngineError, VoiceError


class MacOSBackend(BaseBackend):
    """
    macOS-specific speech backend providing access to VoiceOver screen reader
    and native macOS speech synthesis via standard system tools.
    """

    def __init__(self) -> None:
        self._active_engine_name = "auto"
        self._current_engine = "None"
        self._rate = 50       # 0..100 mapped to ~100..350 wpm
        self._volume = 100    # 0..100
        self._selected_voice: Optional[Voice] = None
        self._last_process: Optional[subprocess.Popen] = None

        self._resolve_engine()

    def _resolve_engine(self) -> None:
        if self.voiceover_is_available():
            self._current_engine = "VoiceOver"
        elif shutil.which("say"):
            self._current_engine = "macOS Native Speech (say)"
        else:
            self._current_engine = "None"

    @property
    def engine_used(self) -> str:
        return self._current_engine

    def voiceover_is_available(self) -> bool:
        """Check if Apple VoiceOver is currently running."""
        # Fast check via pgrep
        if shutil.which("pgrep"):
            try:
                res = subprocess.run(["pgrep", "-x", "VoiceOver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode == 0:
                    return True
            except Exception:
                pass

        # AppleScript check
        if shutil.which("osascript"):
            try:
                cmd = 'tell application "System Events" to (name of processes) contains "VoiceOver"'
                out = subprocess.check_output(["osascript", "-e", cmd], stderr=subprocess.DEVNULL, timeout=1.0)
                return "true" in out.decode("utf-8", errors="ignore").lower()
            except Exception:
                pass
        return False

    @property
    def current_screen_reader_name(self) -> str:
        return "VoiceOver" if self.voiceover_is_available() else ""

    @property
    def current_screen_reader_id(self) -> int:
        return 200 if self.voiceover_is_available() else -1

    def get_supported_screen_readers(self) -> List[str]:
        return ["VoiceOver"]

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        vo_avail = self.voiceover_is_available()
        return [
            ScreenReaderInfo(
                id=200,
                name="VoiceOver",
                available=vo_avail,
            )
        ]

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
        has_vo = self.voiceover_is_available()
        has_say = bool(shutil.which("say"))
        return {
            "voiceover": {
                "id": 1,
                "name": "Apple VoiceOver",
                "available": has_vo,
            },
            "say": {
                "id": 2,
                "name": "macOS Native Speech (say)",
                "available": has_say,
            },
        }

    def set_engine(self, engine: Union[str, int, ScreenReaderId, ScreenReaderInfo]) -> None:
        if isinstance(engine, ScreenReaderInfo):
            engine = engine.name
        elif isinstance(engine, (int, ScreenReaderId)):
            if int(engine) == 1:
                engine = "voiceover"
            elif int(engine) == 2:
                engine = "say"
            elif int(engine) == 0:
                self.reset_engine()
                return
            else:
                raise EngineError(f"Engine ID {engine} is not recognized on macOS.")

        eng_str = str(engine).strip().lower()
        if eng_str in ("auto", "0", "default", "none"):
            self.reset_engine()
            return
        elif eng_str in ("voiceover", "voice over", "vo") or "voiceover" in eng_str or "voice over" in eng_str:
            if not self.voiceover_is_available():
                raise EngineError("VoiceOver is not currently running.")
            self._active_engine_name = "voiceover"
            self._current_engine = "VoiceOver"
        elif "say" in eng_str or "native" in eng_str:
            if not shutil.which("say"):
                raise EngineError("The 'say' command is not available on this macOS system.")
            self._active_engine_name = "say"
            self._current_engine = "macOS Native Speech (say)"
        else:
            raise EngineError(f"Unsupported speech engine: {engine}")

    def reset_engine(self) -> None:
        self._active_engine_name = "auto"
        self._resolve_engine()

    def say(self, msg: str, interrupt: bool = True) -> int:
        if interrupt:
            self.stop()

        target = self._active_engine_name

        # If auto or voiceover requested, try VoiceOver first
        if target in ("auto", "voiceover") and self.voiceover_is_available():
            if shutil.which("osascript"):
                try:
                    # Escape quotes and backslashes for AppleScript string literal
                    escaped = msg.replace("\\", "\\\\").replace('"', '\\"')
                    script = f'tell application "VoiceOver" to output "{escaped}"'
                    res = subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2.0)
                    if res.returncode == 0:
                        return 1
                except Exception:
                    pass

        # Native /say fallback
        if target in ("auto", "say") and shutil.which("say"):
            try:
                # Map rate 0..100 to ~100..350 wpm (default is ~175)
                wpm = int(100 + (self._rate / 100.0) * 250)
                cmd = ["say", "-r", str(wpm)]
                if self._selected_voice:
                    cmd.extend(["-v", self._selected_voice.name])

                # Apply volume via embedded speech synthesis control [[volm X]] (0.0 to 1.0)
                vol_factor = max(0.0, min(1.0, round(self._volume / 100.0, 2)))
                cmd.append(f"[[volm {vol_factor}]] {msg}")

                self._last_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return 1
            except Exception:
                pass

        return 0

    def stop(self) -> int:
        success = False
        # Stop VoiceOver speech
        if self.voiceover_is_available() and shutil.which("osascript"):
            try:
                script = 'tell application "VoiceOver" to output ""'
                res = subprocess.run(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.0)
                if res.returncode == 0:
                    success = True
            except Exception:
                pass

        # Stop say process spawned by this instance
        if self._last_process and self._last_process.poll() is None:
            try:
                self._last_process.terminate()
                self._last_process.wait(timeout=1.0)
                self._last_process = None
                success = True
            except Exception:
                pass

        return 1 if success else 0

    def close(self) -> None:
        if self._last_process:
            try:
                if self._last_process.poll() is None:
                    self._last_process.terminate()
                    self._last_process.wait(timeout=1.0)
            except Exception:
                pass
            self._last_process = None

    @property
    def wait_supported(self) -> bool:
        if self._active_engine_name == "voiceover" or (self._active_engine_name == "auto" and self.voiceover_is_available()):
            return False
        return bool(shutil.which("say"))

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        if not self.wait_supported:
            return False
        if self._last_process:
            try:
                timeout = timeout_ms / 1000.0 if timeout_ms is not None else None
                self._last_process.wait(timeout=timeout)
                self._last_process = None
                return True
            except Exception:
                return False
        return True

    # Rate
    @property
    def rate_supported(self) -> bool:
        return True

    def get_rate(self) -> int:
        return self._rate

    def set_rate(self, rate: int, min_rate: Optional[int] = None, max_rate: Optional[int] = None) -> None:
        self._rate = max(0, min(100, int(rate)))

    @property
    def rate_min(self) -> int:
        return 0

    @property
    def rate_max(self) -> int:
        return 100

    # Volume
    @property
    def volume_supported(self) -> bool:
        return True

    def get_volume(self) -> int:
        return self._volume

    def set_volume(self, volume: int, min_volume: Optional[int] = None, max_volume: Optional[int] = None) -> None:
        self._volume = max(0, min(100, int(volume)))

    @property
    def volume_min(self) -> int:
        return 0

    @property
    def volume_max(self) -> int:
        return 100

    # Pitch (say command doesn't have direct pitch flag)
    @property
    def pitch_supported(self) -> bool:
        return False

    # Voices
    @property
    def voice_supported(self) -> bool:
        return bool(shutil.which("say"))

    def get_voices(self) -> List[Voice]:
        """Parse available macOS voices via `say -v '?'`."""
        if not shutil.which("say"):
            return []
        try:
            out = subprocess.check_output(["say", "-v", "?"], stderr=subprocess.DEVNULL, timeout=3.0)
            lines = out.decode("utf-8", errors="ignore").splitlines()
            voices: List[Voice] = []
            for line in lines:
                line = line.strip()
                if not line or "#" not in line:
                    continue
                # Line format: "Name       locale    # Example"
                left, _, description = line.partition("#")
                parts = left.split()
                if len(parts) >= 2:
                    locale = parts[-1]
                    name = " ".join(parts[:-1])
                    voices.append(Voice(id=len(voices), name=name, language=locale))
            return voices
        except Exception:
            return []

    def get_voice(self) -> Optional[Voice]:
        if self._selected_voice:
            return self._selected_voice
        voices = self.get_voices()
        if not voices:
            return None
        # Try finding system default voice via defaults read com.apple.speech.voice.prefs SelectedVoiceName
        try:
            if shutil.which("defaults"):
                def_name = subprocess.check_output(
                    ["defaults", "read", "com.apple.speech.voice.prefs", "SelectedVoiceName"],
                    stderr=subprocess.DEVNULL,
                    timeout=1.0,
                ).decode("utf-8", errors="ignore").strip()
                if def_name:
                    for v in voices:
                        if v.name.lower() == def_name.lower():
                            return v
        except Exception:
            pass
        return voices[0]

    def set_voice(self, voice: Union[Voice, int, str]) -> None:
        voices = self.get_voices()
        if isinstance(voice, Voice):
            self._selected_voice = voice
            return
        elif isinstance(voice, int):
            for v in voices:
                if v.id == voice:
                    self._selected_voice = v
                    return
            raise VoiceError(f"No voice found with index {voice}")
        elif isinstance(voice, str):
            for v in voices:
                if v.name.lower() == voice.lower() or voice.lower() in v.name.lower():
                    self._selected_voice = v
                    return
            raise VoiceError(f"No voice found matching name {voice!r}")
        else:
            raise VoiceError(f"Invalid voice type: {type(voice)}")

    # Diagnostics
    def get_diagnostics(self) -> Dict[str, Any]:
        active_voice = self.get_voice() if self.voice_supported else None
        voices = self.get_voices() if self.voice_supported else []
        return {
            "platform": "darwin",
            "backend": "MacOSBackend",
            "engine_used": self.engine_used,
            "active_screen_reader_name": self.current_screen_reader_name,
            "active_screen_reader_id": self.current_screen_reader_id,
            "screen_readers": [
                {
                    "id": r.id,
                    "name": r.name,
                    "available": r.available,
                    "version": None,
                }
                for r in self.get_screen_readers()
            ],
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
                "rate": self.get_rate(),
                "rate_range": self.rate_range,
                "volume": self.get_volume(),
                "volume_range": self.volume_range,
                "pitch": None,
                "pitch_range": None,
                "inflection": None,
                "inflection_range": None,
                "is_busy": False,
                "is_paused": False,
            },
            "active_voice": {
                "id": active_voice.id,
                "name": active_voice.name,
            } if active_voice else None,
            "voices_count": len(voices),
        }
