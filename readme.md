# PythonUniversalSpeech

## Overview:

The PythonUniversalSpeech library is a Python interface for interacting with the UniversalSpeech DLL, providing convenient functionality for speech synthesis and braille display. This library is compatible with both 32-bit and 64-bit versions of Python on Windows.

UniversalSpeech aims to streamline and simplify access to speech within applications. It accomplishes this by providing a unified interface that allows speech to be achieved through various means, including active screen readers, direct synthesis, or native/OS speech engines. The library dynamically adapts based on what is available and supported, offering a cohesive and versatile solution for speech-related functionalities.

PythonUniversalSpeech is built upon UniversalSpeech, initially developed by [qtnc](https://github.com/qtnc). To learn more about the project and its details, you can visit the [UniversalSpeech GitHub repository](https://github.com/qtnc/UniversalSpeech).

## Supported engines:

- Jaws for Windows
- NVDA 2011.1 or above
- Windows-Eyes
- System Access
- Dolphin Supernova
- ZoomText
- Cobra (partially)
- Windows Narrator
- SAPI 5

## Installation:

To install the UniversalSpeech library, you can use the following pip command:

```bash
pip install UniversalSpeech
```

Alternatively, you can download the project directly from the GitHub repository and use it in your Python project.

## Usage:

### Using as a Context Manager (Recommended in 2.0+):

```python
from UniversalSpeech import UniversalSpeech

with UniversalSpeech() as speech:
    speech.say("Hello from UniversalSpeech!")
    speech.wait()
```

### UniversalSpeech Class Reference:

#### Properties:
- `engine_used` (str): Name of the currently active speech engine.
- `current_screen_reader_name` (str): Name of the active screen reader (e.g. `NVDA`, `Jaws`, `SAPI5`).
- `current_screen_reader_id` (int): Integer ID of the active screen reader.
- `current_voice` (Optional[Voice]): Currently selected voice object.
- `voice_supported` (bool): Whether changing voices is supported by the current engine.
- `is_busy` (bool): Whether speech is currently in progress.
- `busy_supported` (bool): Whether checking busy status is supported.
- `is_paused` (bool): Whether speech playback is paused.
- `pause_supported` (bool): Whether pausing speech is supported.
- `wait_supported` (bool): Whether waiting for speech completion is supported.
- `rate_supported` (bool): Whether setting speech rate is supported.
- `volume_supported` (bool): Whether setting speech volume is supported.
- `pitch_supported` (bool): Whether setting speech pitch is supported.
- `inflection_supported` (bool): Whether setting speech inflection is supported.

#### Speech & Braille Methods:
- `say(msg: str, interrupt: bool = True) -> None`: Speaks message using the active engine.
- `say_a(msg: str, interrupt: bool = True) -> None`: Speaks the first letter/character of the message.
- `braille(msg: str) -> None`: Displays message on connected braille display.
- `speech(msg: str) -> None`: Performs both speech and braille display.
- `speech_a(msg: str) -> None`: Performs both `say_a` and braille display.
- `stop() -> None`: Immediately stops speech.
- `close() -> None`: Stops speech and cleans up resources.
- `say_ssml(ssml: str) -> bool`: Speaks XML/SSML formatted text if supported.

#### Playback & Flow Control:
- `wait(timeout_ms: Optional[int] = None) -> bool`: Waits for speech playback to finish.
- `pause(paused: bool = True) -> None`: Pauses or unpauses speech playback.
- `resume() -> None`: Resumes paused speech playback.
- `reset_engine() -> None`: Restores default automatic engine selection.

#### Voice & Engine Configuration:
- `get_voices() -> List[Voice]`: Returns list of available voices.
- `get_voice() -> Optional[Voice]`: Returns the currently active voice.
- `set_voice(voice: Union[int, str, Voice]) -> None`: Sets active voice by index, name, or Voice instance.
- `get_engines() -> Dict[str, Dict]`: Returns dictionary of all engines with availability status.
- `set_engine(engine: str) -> None`: Sets speech engine to the specified engine name.
- `enable_native_speech(enabled: bool = True) -> None`: Enables or disables fallback to native OS engines (SAPI5).

#### Screen Reader Information:
- `get_supported_screen_readers() -> List[str]`: List of all 10 supported screen readers.
- `get_screen_readers() -> List[ScreenReaderInfo]`: List of ScreenReaderInfo objects with availability.
- `nvda_is_available() -> bool`: True if NVDA is running.
- `jaws_is_available() -> bool`: True if JAWS is running.
- `sapi_is_available() -> bool`: True if SAPI5 is available.
- `system_access_is_available() -> bool`: True if System Access is running.
- `supernova_is_available() -> bool`: True if Dolphin Supernova is running.
- `window_eyes_is_available() -> bool`: True if Window-Eyes is running.
- `cobra_is_available() -> bool`: True if Cobra is running.
- `zoomtext_is_available() -> bool`: True if ZoomText is running.
- `narrator_is_available() -> bool`: True if Windows Narrator is running.
- `nvda_get_version() -> Optional[str]`: Returns NVDA version string if running (e.g. '2026.2'), else None.
- `jfw_get_version() -> Optional[str]`: Returns JAWS version string if running (e.g. '2025.0'), else None.

## Command-Line Interface (CLI):

UniversalSpeech can be run directly from the terminal:

```bash
# Speak a message
python -m UniversalSpeech "Hello world"

# Speak and display on braille
python -m UniversalSpeech "Hello" --braille

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
- `DLLFileNotFoundError`: Raised when required DLL files are missing.
- `UnsupportedError`: Raised when a feature is unsupported by the active engine.
- `EngineError`: Raised when an invalid engine is requested.
- `VoiceError`: Raised when an invalid voice is requested.

## Migration Guide: Modern API vs. Legacy Methods

UniversalSpeech 2.0.0 is a major modernization release. While **both legacy methods and the modern API work fully side-by-side** to ensure 100% backward compatibility, older low-level procedural patterns and parameter getter/setter methods are scheduled for future deprecation.

Users and maintainers are strongly encouraged to upgrade to the modern API, which is cleaner, safer, and fully typed.

### Comparison Table

| Feature | Legacy Method (Deprecated soon) | Modern API (Recommended in 2.0+) | Rationale |
| :--- | :--- | :--- | :--- |
| **Lifecycle** | `speech = UniversalSpeech()` | `with UniversalSpeech() as speech:` | Automatic speech stop and resource cleanup on exit |
| **Speech Rate** | `speech.set_value(RATE, val)` | `speech.set_rate(val)` | Dedicated method with range and support validation |
| **Rate Check** | `speech.get_value(RATE_SUPPORTED)` | `speech.rate_supported` | Intuitive boolean property |
| **Volume** | `speech.set_value(VOLUME, val)` | `speech.set_volume(val)` | Safe 0–100 volume setter |
| **Volume Check** | `speech.get_value(VOLUME_SUPPORTED)` | `speech.volume_supported` | Intuitive boolean property |
| **Pitch** | `speech.set_value(PITCH, val)` | `speech.set_pitch(val)` | Dedicated method with support check |
| **Pitch Check** | `speech.get_value(PITCH_SUPPORTED)` | `speech.pitch_supported` | Intuitive boolean property |
| **Inflection** | `speech.set_value(INFLECTION, val)` | `speech.set_inflection(val)` | Clean setter method |
| **Wait** | `speech.get_value(WAIT)` / `setValue(WAIT, ms)` | `speech.wait(timeout_ms)` | Clear, blocking synchronization method |
| **Busy Check** | `speech.get_value(BUSY)` | `speech.is_busy` | Simple boolean property |
| **Pause / Resume**| `speech.set_value(PAUSED, 1/0)` | `speech.pause()` / `speech.resume()` | Standard audio playback API ergonomics |
| **Paused Check** | `speech.get_value(PAUSED)` | `speech.is_paused` | Simple boolean property |
| **Voices** | `speech.get_string(SP_VOICE + i)` | `speech.get_voices()` / `speech.set_voice('Zira')` | Structured `Voice` objects with substring search |
| **Screen Readers**| `speech.get_string(SP_ENGINE + i)` | `speech.get_screen_readers()` | Typed `ScreenReaderInfo` with active status |
| **Reader Check** | Custom loops / ID checks | `speech.nvda_is_available()`, etc. | Direct, instant availability methods |
| **Reader Version**| N/A (Direct DLL export) | `speech.nvda_get_version()`, `speech.jfw_get_version()` | Instant version string query |
| **Constants** | `from UniversalSpeech import VOLUME, ...` | `from UniversalSpeech import SpeechParam` | Structured, autocomplete-friendly `IntEnum` |
| **ANSI Speech** | `speech.sayA("msg")` | `speech.say_a("msg")` | Consistent snake_case naming |

## Credits & Attribution

`PythonUniversalSpeech` is an enhanced Python SDK and wrapper built upon the original C library **UniversalSpeech**, created by **Quentin Cosendey (QuentinC)**.

- **Original C Repository**: [qtnc/UniversalSpeech on GitHub](https://github.com/qtnc/UniversalSpeech)
- **Official Website & Documentation**: [QuentinC's Web Corner (UniversalSpeech)](http://quentinc.net/universalspeech/)
- **Original License**: [MIT License](https://github.com/qtnc/UniversalSpeech/blob/master/LICENSE.txt)

We express our deep appreciation to **Quentin Cosendey** and contributors across the screen reader accessibility and audio game communities for establishing the foundational cross-screen-reader C architecture.

## Contributing

For information on running tests, building distributions, and the automated PyPI release process, please see [CONTRIBUTING.md](CONTRIBUTING.md).
