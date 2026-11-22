"""
Linux backend for UniversalSpeech supporting Speech Dispatcher (SSIP/socket/cli),
eSpeak/eSpeak-ng (library/cli), and Orca detection with zero external dependencies.
"""
import os
import sys
import socket
import shutil
import subprocess
import ctypes
import threading
from typing import Optional, Dict, Any, Union, List, Tuple
from .base import BaseBackend
from ..voices import Voice
from ..screen_readers import ScreenReaderInfo
from ..constants import ScreenReaderId
from ..exceptions import UnsupportedError, EngineError


class _SSIPSocketClient:
    """Minimal zero-dependency SSIP client communicating directly over Unix socket or TCP."""

    def __init__(self, socket_path: Optional[str] = None, port: Optional[int] = None) -> None:
        self.sock: Optional[socket.socket] = None
        self._connected = False
        self._connect(socket_path, port)

    def _connect(self, socket_path: Optional[str], port: Optional[int]) -> None:
        try:
            if socket_path and hasattr(socket, "AF_UNIX") and os.path.exists(socket_path):
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.settimeout(2.0)
                self.sock.connect(socket_path)
            elif port:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(2.0)
                self.sock.connect(("127.0.0.1", port))
            else:
                return

            # Read greeting
            resp = self._read_response()
            if not resp or not resp.startswith("2"):
                self.close()
                return

            # Set client name
            self._send_command('SET self CLIENT_NAME "user:UniversalSpeech:app"')
            self._connected = True
        except Exception:
            self.close()

    def _send_command(self, cmd: str) -> Optional[str]:
        if not self.sock:
            return None
        try:
            self.sock.sendall((cmd + "\r\n").encode("utf-8"))
            return self._read_response()
        except Exception:
            self.close()
            return None

    def _read_response(self) -> Optional[str]:
        if not self.sock:
            return None
        try:
            data = b""
            while True:
                chunk = self.sock.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\r\n" in data:
                    break
            return data.decode("utf-8", errors="replace").strip()
        except Exception:
            return None

    def speak(self, text: str) -> bool:
        if not self._connected or not self.sock:
            return False
        try:
            self.sock.sendall(b"SPEAK\r\n")
            # In SSIP, a single dot on a line terminates speech
            safe_text = text.replace("\r", "").replace("\n.", "\n..")
            self.sock.sendall(safe_text.encode("utf-8") + b"\r\n.\r\n")
            resp = self._read_response()
            return bool(resp and resp.startswith("2"))
        except Exception:
            self.close()
            return False

    def cancel(self) -> bool:
        resp = self._send_command("CANCEL self")
        return bool(resp and resp.startswith("2"))

    def stop(self) -> bool:
        resp = self._send_command("STOP self")
        return bool(resp and resp.startswith("2"))

    def set_rate(self, rate: int) -> None:
        # SSIP rate is -100 to 100
        val = max(-100, min(100, rate))
        self._send_command(f"SET self RATE {val}")

    def set_volume(self, volume: int) -> None:
        # SSIP volume is -100 to 100
        val = max(-100, min(100, volume))
        self._send_command(f"SET self VOLUME {val}")

    def set_pitch(self, pitch: int) -> None:
        # SSIP pitch is -100 to 100
        val = max(-100, min(100, pitch))
        self._send_command(f"SET self PITCH {val}")

    def close(self) -> None:
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected


class LinuxBackend(BaseBackend):
    """
    Linux-specific speech backend providing access to Speech Dispatcher,
    eSpeak/eSpeak-ng, and Orca screen reader detection.
    """

    _espeak_lock = threading.Lock()
    _cached_espeak_lib: Optional[ctypes.CDLL] = None
    _espeak_initialized: bool = False

    def __init__(self) -> None:
        self._active_engine_name = "auto"
        self._current_engine = "None"
        self._rate = 50
        self._volume = 100
        self._pitch = 50

        # Subprocess tracking for audio/cli
        self._last_process: Optional[subprocess.Popen] = None

        # Speech Dispatcher SSIP socket client
        self._ssip_client: Optional[_SSIPSocketClient] = None
        self._init_speechd()

        # eSpeak library or binary
        self._espeak_lib: Optional[ctypes.CDLL] = None
        self._init_espeak()

        # Determine default active engine
        self._resolve_engine()

    def _init_speechd(self) -> None:
        """Find and connect to Speech Dispatcher socket or fallback to port."""
        if hasattr(socket, "AF_UNIX"):
            xdg = os.environ.get("XDG_RUNTIME_DIR", "")
            uid = os.getuid() if hasattr(os, "getuid") else 1000
            user = os.environ.get("USER", "root")
            candidates = [
                os.environ.get("SPEECHD_SOCKET"),
                os.path.join(xdg, "speech-dispatcher", "speechd.sock") if xdg else None,
                f"/run/user/{uid}/speech-dispatcher/speechd.sock",
                f"/tmp/speechd-{user}/speechd.sock",
            ]
            for path in candidates:
                if path and os.path.exists(path):
                    client = _SSIPSocketClient(socket_path=path)
                    if client.is_connected:
                        self._ssip_client = client
                        return

        # Fallback to TCP port 6560
        client = _SSIPSocketClient(port=6560)
        if client.is_connected:
            self._ssip_client = client

    def _init_espeak(self) -> None:
        """Attempt to load libespeak-ng or libespeak via ctypes safely with process-level caching."""
        with LinuxBackend._espeak_lock:
            if LinuxBackend._espeak_initialized:
                self._espeak_lib = LinuxBackend._cached_espeak_lib
                return

            for libname in ("libespeak-ng.so.1", "libespeak-ng.so", "libespeak.so.1", "libespeak.so"):
                try:
                    lib = ctypes.cdll.LoadLibrary(libname)
                    # Initialize espeak: 2 = AUDIO_OUTPUT_PLAYBACK
                    if hasattr(lib, "espeak_Initialize"):
                        res = lib.espeak_Initialize(2, 0, None, 0)
                        if res != -1:
                            LinuxBackend._cached_espeak_lib = lib
                            LinuxBackend._espeak_initialized = True
                            self._espeak_lib = lib
                            return
                except Exception:
                    continue

            LinuxBackend._espeak_initialized = True

    def _resolve_engine(self) -> None:
        """Determine which speech engine to use based on availability."""
        if self._ssip_client and self._ssip_client.is_connected:
            self._current_engine = "Speech Dispatcher (SSIP)"
        elif shutil.which("spd-say"):
            self._current_engine = "Speech Dispatcher (CLI)"
        elif self._espeak_lib:
            self._current_engine = "eSpeak (Library)"
        elif shutil.which("espeak-ng"):
            self._current_engine = "eSpeak-ng (CLI)"
        elif shutil.which("espeak"):
            self._current_engine = "eSpeak (CLI)"
        else:
            self._current_engine = "None"

    @property
    def engine_used(self) -> str:
        return self._current_engine

    def get_engines(self) -> Dict[str, Dict[str, Any]]:
        has_spd = bool((self._ssip_client and self._ssip_client.is_connected) or shutil.which("spd-say"))
        has_espeak = bool((self._espeak_lib is not None) or shutil.which("espeak-ng") or shutil.which("espeak"))
        return {
            "speech-dispatcher": {
                "id": 1,
                "name": "Speech Dispatcher",
                "available": has_spd,
            },
            "espeak": {
                "id": 2,
                "name": "eSpeak / eSpeak-ng",
                "available": has_espeak,
            },
        }

    def set_engine(self, engine: Union[str, int, ScreenReaderId, ScreenReaderInfo]) -> None:
        if isinstance(engine, ScreenReaderInfo):
            engine = engine.name
        elif isinstance(engine, (int, ScreenReaderId)):
            if int(engine) == 1:
                engine = "speech-dispatcher"
            elif int(engine) == 2:
                engine = "espeak"
            elif int(engine) == 0:
                self.reset_engine()
                return
            else:
                raise EngineError(f"Engine ID {engine} is not recognized on Linux.")

        eng_str = str(engine).strip().lower()
        if eng_str in ("auto", "0", "default", "none"):
            self.reset_engine()
            return
        elif "speech" in eng_str or "dispatcher" in eng_str or "spd" in eng_str:
            if not ((self._ssip_client and self._ssip_client.is_connected) or shutil.which("spd-say")):
                raise EngineError("Speech Dispatcher is not available on this system.")
            self._active_engine_name = "speech-dispatcher"
            self._current_engine = "Speech Dispatcher"
        elif "espeak" in eng_str:
            if not ((self._espeak_lib is not None) or shutil.which("espeak-ng") or shutil.which("espeak")):
                raise EngineError("eSpeak is not available on this system.")
            self._active_engine_name = "espeak"
            self._current_engine = "eSpeak"
        else:
            raise EngineError(f"Unsupported speech engine: {engine}")

    def reset_engine(self) -> None:
        self._active_engine_name = "auto"
        self._resolve_engine()

    def say(self, msg: str, interrupt: bool = True) -> int:
        if interrupt:
            self.stop()

        target = self._active_engine_name

        # Speech Dispatcher
        if target in ("auto", "speech-dispatcher"):
            if self._ssip_client and self._ssip_client.is_connected:
                # Map rate (0..100) to SSIP (-100..100)
                ssip_rate = int((self._rate - 50) * 2)
                ssip_vol = int((self._volume - 50) * 2)
                ssip_pitch = int((self._pitch - 50) * 2)
                self._ssip_client.set_rate(ssip_rate)
                self._ssip_client.set_volume(ssip_vol)
                self._ssip_client.set_pitch(ssip_pitch)
                if self._ssip_client.speak(msg):
                    return 1

            if shutil.which("spd-say"):
                try:
                    spd_rate = int((self._rate - 50) * 2)
                    spd_pitch = int((self._pitch - 50) * 2)
                    spd_vol = int((self._volume - 50) * 2)
                    self._last_process = subprocess.Popen(
                        ["spd-say", "-r", str(spd_rate), "-p", str(spd_pitch), "-i", str(spd_vol), "--", msg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return 1
                except Exception:
                    pass

        # eSpeak / eSpeak-ng
        if target in ("auto", "espeak"):
            if self._espeak_lib and hasattr(self._espeak_lib, "espeak_Synth"):
                try:
                    with LinuxBackend._espeak_lock:
                        # espeakRate range ~80 to ~450 wpm, map 0..100 -> 80..380
                        wpm = int(80 + (self._rate / 100.0) * 300)
                        if hasattr(self._espeak_lib, "espeak_SetParameter"):
                            # espeakRATE = 1, espeakVOLUME = 2, espeakPITCH = 3
                            self._espeak_lib.espeak_SetParameter(1, wpm, 0)
                            self._espeak_lib.espeak_SetParameter(2, self._volume, 0)
                            self._espeak_lib.espeak_SetParameter(3, self._pitch, 0)

                        msg_bytes = msg.encode("utf-8")
                        # POS_CHARACTER = 1, SEARCH_NORMAL = 0
                        self._espeak_lib.espeak_Synth(msg_bytes, len(msg_bytes) + 1, 0, 1, 0, 0x1000, None, None)
                    return 1
                except Exception:
                    pass

            espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
            if espeak_bin:
                try:
                    wpm = int(80 + (self._rate / 100.0) * 300)
                    self._last_process = subprocess.Popen(
                        [espeak_bin, "-s", str(wpm), "-a", str(self._volume), "-p", str(self._pitch), msg],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return 1
                except Exception:
                    pass

        return 0

    def stop(self) -> int:
        success = False
        if self._ssip_client and self._ssip_client.is_connected:
            if self._ssip_client.cancel():
                success = True

        if shutil.which("spd-say"):
            try:
                subprocess.run(["spd-say", "--cancel"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1.0)
                success = True
            except Exception:
                pass

        if self._espeak_lib and hasattr(self._espeak_lib, "espeak_Cancel"):
            try:
                with LinuxBackend._espeak_lock:
                    self._espeak_lib.espeak_Cancel()
                success = True
            except Exception:
                pass

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
        self.stop()
        if self._last_process:
            try:
                if self._last_process.poll() is None:
                    self._last_process.terminate()
                    self._last_process.wait(timeout=1.0)
            except Exception:
                pass
            self._last_process = None
        if self._ssip_client:
            self._ssip_client.close()
            self._ssip_client = None

    @property
    def wait_supported(self) -> bool:
        return True

    def wait(self, timeout_ms: Optional[int] = None) -> bool:
        if self._last_process:
            try:
                timeout = timeout_ms / 1000.0 if timeout_ms is not None else None
                self._last_process.wait(timeout=timeout)
                self._last_process = None
                return True
            except Exception:
                return False
        return True

    # Parameters
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

    @property
    def pitch_supported(self) -> bool:
        return True

    def get_pitch(self) -> int:
        return self._pitch

    def set_pitch(self, pitch: int, min_pitch: Optional[int] = None, max_pitch: Optional[int] = None) -> None:
        self._pitch = max(0, min(100, int(pitch)))

    @property
    def pitch_min(self) -> int:
        return 0

    @property
    def pitch_max(self) -> int:
        return 100

    # Screen Reader: Orca
    def orca_is_available(self) -> bool:
        """Check if Orca screen reader is running on Linux."""
        try:
            # Check pgrep
            if shutil.which("pgrep"):
                res = subprocess.run(["pgrep", "-x", "orca"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if res.returncode == 0:
                    return True
            # Check /proc
            if os.path.exists("/proc"):
                for pid in os.listdir("/proc"):
                    if not pid.isdigit():
                        continue
                    try:
                        with open(f"/proc/{pid}/comm", "r", encoding="utf-8", errors="ignore") as f:
                            if "orca" in f.read().lower():
                                return True
                    except (OSError, IOError):
                        continue
        except Exception:
            pass
        return False

    @property
    def current_screen_reader_name(self) -> str:
        if self.orca_is_available():
            return "Orca"
        return ""

    @property
    def current_screen_reader_id(self) -> int:
        if self.orca_is_available():
            return 100
        return 0

    def get_supported_screen_readers(self) -> List[str]:
        return ["Orca"]

    def get_screen_readers(self) -> List[ScreenReaderInfo]:
        orca_avail = self.orca_is_available()
        return [
            ScreenReaderInfo(
                id=100,
                name="Orca",
                available=orca_avail,
            )
        ]

    def orca_get_version(self) -> Optional[str]:
        """Query Orca version if available."""
        if shutil.which("orca"):
            try:
                out = subprocess.check_output(["orca", "--version"], stderr=subprocess.DEVNULL, timeout=2.0)
                text = out.decode("utf-8", errors="ignore").strip()
                # Orca version output usually: "Orca 45.1" or "45.1"
                parts = text.split()
                return parts[-1] if parts else text
            except Exception:
                pass
        return None

    # Diagnostics
    def get_diagnostics(self) -> Dict[str, Any]:
        orca_ver = self.orca_get_version() if self.orca_is_available() else None
        return {
            "platform": "linux",
            "backend": "LinuxBackend",
            "engine_used": self.engine_used,
            "active_screen_reader_name": self.current_screen_reader_name,
            "active_screen_reader_id": self.current_screen_reader_id,
            "screen_readers": [
                {
                    "id": r.id,
                    "name": r.name,
                    "available": r.available,
                    "version": orca_ver if r.name == "Orca" else None,
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
                "pitch": self.get_pitch(),
                "pitch_range": self.pitch_range,
                "inflection": None,
                "inflection_range": None,
                "is_busy": False,
                "is_paused": False,
            },
            "active_voice": None,
            "voices_count": 0,
        }
