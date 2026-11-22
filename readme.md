# PythonUniversalSpeech

## Overview:

`PythonUniversalSpeech` is a high-level, cross-platform Python SDK and interface for speech synthesis, screen readers, and braille displays across **Windows**, **Linux**, and **macOS** with **zero external dependencies**.

UniversalSpeech aims to streamline and simplify speech output in applications by providing a single, unified interface. It dynamically selects the best available engine on the host operating system:
- **Windows**: Interfaces directly with screen readers (NVDA, JAWS, Narrator, SuperNova, etc.) and native SAPI 5 via `UniversalSpeech.dll`.
- **Linux**: Connects directly to Speech Dispatcher (via native SSIP Unix socket or CLI `spd-say`), eSpeak-ng / eSpeak, and detects the Orca screen reader.
- **macOS**: Drives Apple VoiceOver and native system speech synthesis (`say`) with full voice and locale discovery.

PythonUniversalSpeech is built upon UniversalSpeech, initially developed by [qtnc](https://github.com/qtnc/UniversalSpeech).

## Supported Platforms & Engines:

### Windows:
- NVDA (2011.1+)
- JAWS for Windows (including scripting & settings paths)
- Windows Narrator
- SAPI 5 (Speech API)
- Dolphin Supernova
- ZoomText
- System Access
- Window-Eyes
- Cobra (partially)

### Linux:
- Speech Dispatcher (zero-dependency native SSIP socket communication or `spd-say`)
- eSpeak-ng / eSpeak (native shared library or CLI)
- Orca screen reader detection and version query

### macOS:
- Apple VoiceOver (speech & silence via AppleScript)
- macOS Native Speech (`say`) with voice and language/locale discovery

## Installation:

```bash
pip install UniversalSpeech
```

*Requirements*: Python 3.7+ on Windows, Linux, or macOS. No external packages (like `pywin32` or `appscript`) are required.

## Usage:

### Using as a Context Manager (Recommended in 2.0+ / 3.0+):

```python
from UniversalSpeech import UniversalSpeech

with UniversalSpeech() as speech:
    speech.say("Hello from UniversalSpeech v3.0!")
    speech.wait()
```

### UniversalSpeech Class Reference:

#### Properties:
- `engine_used` (str): Name of the currently active speech engine.
- `current_screen_reader_name` (str): Name of the active screen reader (e.g. `NVDA`, `JAWS`, `Orca`, `VoiceOver`).
- `current_screen_reader_id` (int): Integer ID of the active screen reader.
- `current_voice` (Optional[Voice]): Currently selected voice object.
- `voice_supported` (bool): Whether changing voices is supported by the current engine.
- `is_busy` (bool): Whether speech is currently in progress.
- `busy_supported` (bool): Whether checking busy status is supported.
- `is_paused` (bool): Whether speech playback is paused.
- `pause_supported` (bool): Whether pausing speech is supported.
- `wait_supported` (bool): Whether waiting for speech completion is supported.
- `rate` (int): Property getter and setter for speech rate.
- `rate_supported` (bool): Whether setting speech rate is supported.
- `rate_min` / `rate_max` (int): Minimum and maximum speech rate for active engine.
- `rate_range` (Tuple[int, int]): Tuple of `(rate_min, rate_max)`.
- `volume` (int): Property getter and setter for speech volume.
- `volume_supported` (bool): Whether setting speech volume is supported.
- `volume_min` / `volume_max` (int): Minimum and maximum speech volume for active engine.
- `volume_range` (Tuple[int, int]): Tuple of `(volume_min, volume_max)`.
- `pitch` (int): Property getter and setter for speech pitch.
- `pitch_supported` (bool): Whether setting speech pitch is supported.
- `pitch_min` / `pitch_max` (int): Minimum and maximum speech pitch for active engine.
- `pitch_range` (Tuple[int, int]): Tuple of `(pitch_min, pitch_max)`.
- `inflection` (int): Property getter and setter for speech inflection.
- `inflection_supported` (bool): Whether setting speech inflection is supported.
- `inflection_min` / `inflection_max` (int): Minimum and maximum speech inflection for active engine.
- `inflection_range` (Tuple[int, int]): Tuple of `(inflection_min, inflection_max)`.

#### Speech & Braille Methods:
- `say(msg: str, interrupt: bool = True) -> int`: Speaks message using the active engine (full Unicode).
- `say_a(msg: str, interrupt: bool = True) -> int`: Speaks ANSI message using legacy `speechSayA`.
- `braille(msg: str) -> int`: Displays message on connected braille display.
- `speech(msg: str, interrupt: bool = True) -> None`: Performs both speech and braille display.
- `speech_a(msg: str, interrupt: bool = True) -> None`: Performs both `say_a` and braille display.
- `stop() -> int`: Immediately stops speech.
- `close() -> None`: Stops speech and cleans up resources.
- `say_ssml(ssml: str) -> bool`: Speaks XML/SSML formatted text if supported.

#### Playback & Flow Control:
- `wait(timeout_ms: Optional[int] = None) -> bool`: Waits for speech playback to finish.
- `pause(paused: bool = True) -> None`: Pauses or unpauses speech playback.
- `resume() -> None`: Resumes paused speech playback.
- `reset_engine() -> None`: Restores default automatic engine selection.

#### Voice & Engine Configuration:
- `get_voices() -> List[Voice]`: Returns list of available voices (`id`, `name`, optional `language`).
- `get_voice() -> Optional[Voice]`: Returns the currently active voice.
- `set_voice(voice: Union[int, str, Voice]) -> None`: Sets active voice by index, name, or Voice instance.
- `get_engines() -> Dict[str, Dict]`: Returns dictionary of all engines with availability status.
- `set_engine(engine: Union[str, int, ScreenReaderId]) -> None`: Sets speech engine by name (case-insensitive), integer ID, or enum.
- `enable_native_speech(enabled: bool = True) -> None`: Enables or disables fallback to native OS engines.

#### Windows Screen Readers:
- `get_supported_screen_readers() -> List[str]`: List of supported screen readers.
- `get_screen_readers() -> List[ScreenReaderInfo]`: List of ScreenReaderInfo objects with availability.
- `nvda_is_available() -> bool`: True if NVDA is running.
- `jaws_is_available() -> bool`: True if JAWS is running.
- `sapi_is_available() -> bool`: True if SAPI5 is available.
- `narrator_is_available() -> bool`: True if Windows Narrator is running.
- `nvda_get_version() -> Optional[str]`: Returns NVDA version string if running (e.g. '2026.2'), else None.
- `jfw_get_version() -> Optional[str]`: Returns JAWS version string if running (e.g. '2025.0'), else None.

#### JAWS Scripting & Extensions:
- `jaws_run_script(script_name: str) -> bool`: Executes a JAWS script by name (e.g. `SayLine`).
- `jaws_run_function(function_call: str) -> bool`: Executes a JAWS function call with arguments.
- `jaws_get_user_settings_directory() -> Optional[str]`: Returns path to the active JAWS user settings folder.

#### System Diagnostics:
- `get_diagnostics() -> Dict[str, Any]`: Returns structured dictionary of system, engine, and voice status.
- `diagnostics_summary() -> str`: Formats diagnostic information as a human-readable text report.

## Command-Line Interface (CLI):

UniversalSpeech can be run directly from the terminal across Windows, Linux, and macOS:

```bash
# Speak a message
python -m UniversalSpeech "Hello world"

# Speak from piped input
echo "Operation completed" | python -m UniversalSpeech

# Speak and display on braille
python -m UniversalSpeech "Hello" --braille

# Adjust rate and volume from CLI
python -m UniversalSpeech "Fast announcement" --rate 120 --volume 90

# Show system and speech engine diagnostics report
python -m UniversalSpeech --diagnostics

# Show currently active engine and screen reader
python -m UniversalSpeech --current

# List available voices
python -m UniversalSpeech --list-voices

# List supported engines and screen readers
python -m UniversalSpeech --list-engines
python -m UniversalSpeech --list-readers
```

## Exceptions:

All exceptions inherit from `UniversalSpeechError`:
- `UniversalSpeechError`: Base exception for the library.
- `DLLFileNotFoundError`: Raised when required DLL files are missing on Windows.
- `PlatformError`: Raised when the library is loaded on an unsupported OS.
- `UnsupportedError`: Raised when a feature is unsupported by the active engine.
- `EngineError`: Raised when an invalid engine is requested.
- `VoiceError`: Raised when an invalid voice is requested.

## Architecture:

UniversalSpeech 3.0 introduces a modular backend architecture:
- `UniversalSpeech.backends.BaseBackend`: Abstract contract defining all speech and control operations.
- `UniversalSpeech.backends.WindowsBackend`: Interfacing with `UniversalSpeech.dll` via ctypes.
- `UniversalSpeech.backends.LinuxBackend`: Interfacing with Speech Dispatcher (SSIP socket / CLI), eSpeak, and Orca.
- `UniversalSpeech.backends.MacOSBackend`: Interfacing with Apple VoiceOver and native macOS `say`.

## Credits & Attribution

`PythonUniversalSpeech` is an enhanced Python SDK and wrapper built upon the original C library **UniversalSpeech**, created by **Quentin Cosendey (QuentinC)**.

- **Original C Repository**: [qtnc/UniversalSpeech on GitHub](https://github.com/qtnc/UniversalSpeech)
- **Official Website & Documentation**: [QuentinC's Web Corner (UniversalSpeech)](http://quentinc.net/universalspeech/)
- **Original License**: [MIT License](https://github.com/qtnc/UniversalSpeech/blob/master/LICENSE.txt)

We express our deep appreciation to **Quentin Cosendey** and contributors across the screen reader accessibility and audio game communities for establishing the foundational cross-screen-reader C architecture.

## Contributing

For information on running tests, building distributions, and the automated PyPI release process, please see [CONTRIBUTING.md](CONTRIBUTING.md).
