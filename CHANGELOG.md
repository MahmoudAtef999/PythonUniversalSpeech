# Changelog

All notable changes to the `PythonUniversalSpeech` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-11-22

### Added
- **Multi-Platform Support**:
  - **Linux Support**: Added `LinuxBackend` supporting Speech Dispatcher via direct SSIP Unix domain socket (`/run/user/<uid>/speech-dispatcher/speechd.sock` or TCP `6560`), `spd-say` CLI fallback, eSpeak-ng / eSpeak (native shared library or CLI), and Orca screen reader detection and version query.
  - **macOS Support**: Added `MacOSBackend` supporting Apple VoiceOver (speech output and silence via built-in AppleScript/`osascript`), native macOS speech synthesis (`/usr/bin/say`), voice discovery with locale detection (`Voice(id, name, language)`), and rate/volume controls.
  - **Zero External Dependencies**: Works purely using the Python standard library (`ctypes`, `socket`, `subprocess`) on all operating systems without requiring `pywin32`, `appscript`, or `python-speechd`.
- **Modular Backend Architecture**:
  - `UniversalSpeech.backends.BaseBackend`: Abstract contract defining all speech operations, parameter queries, screen reader checks, and diagnostics.
  - `UniversalSpeech.backends.WindowsBackend`: Interfacing with `UniversalSpeech.dll` via ctypes for Windows screen readers (NVDA, JAWS, Narrator, SuperNova, etc.).
  - `UniversalSpeech.backends.LinuxBackend`: Implementation for Linux desktop speech synthesis.
  - `UniversalSpeech.backends.MacOSBackend`: Implementation for macOS speech synthesis.
  - Dynamic OS platform detection in `UniversalSpeech` facade with optional backend dependency injection.
- **Pythonic Speech Properties & Range Bounds**:
  - Direct getters and setters for `speech.rate`, `speech.volume`, `speech.pitch`, and `speech.inflection`.
  - Bound tuples: `speech.rate_range`, `speech.volume_range`, `speech.pitch_range`, `speech.inflection_range` returning `(min, max)` tuples.
- **JAWS Scripting API**:
  - `speech.jaws_run_script(script_name: str) -> bool`: Execute JAWS scripts by name.
  - `speech.jaws_run_function(function_call: str) -> bool`: Execute JAWS functions with arguments.
  - `speech.jaws_get_user_settings_directory() -> Optional[str]`: Query active JAWS user settings folder.
  - Backward-compatibility aliases: `jfw_run_script`, `jfw_run_function`, `jfw_get_user_settings_directory`.
- **System Diagnostics & CLI**:
  - `speech.get_diagnostics() -> Dict[str, Any]`: Structured dictionary detailing host OS, backend, active engine, active screen reader with versions, available voices, and supported parameters.
  - `speech.diagnostics_summary() -> str`: Formatted human-readable report.
  - CLI flags: `--diagnostics`, `--current`, `--list-engines`, `--list-readers`, `--list-voices`, `--rate`, `--volume`, `--braille`.
- **Enhanced Engine Selection**:
  - Case-insensitive engine selection in `set_engine()` (e.g. `"sapi5"`, `"SAPI5"`, `"nvda"`, `"speech-dispatcher"`, `"voiceover"`).
  - Support for `ScreenReaderId` enum, `ScreenReaderInfo`, integer IDs, and `"auto"` / `reset_engine()`.
- **Multi-Platform CI Matrix**:
  - Configured GitHub Actions matrix testing against `windows-latest`, `ubuntu-latest`, and `macos-latest` across Python 3.8, 3.9, 3.10, 3.11, 3.12, and 3.13.

### Fixed
- Fixed missing `interrupt` parameter in `speech()` and `speech_a()` methods.
- Fixed redundant DLL reloads in `Loader` by caching loaded CDLL instances.
- Added platform validation in `Loader` to raise descriptive `PlatformError` on unsupported platforms.
- Fixed `say_a()` docstrings and added missing `zdsr_is_available()`.

---

## [2.0.0] - 2026-09-22

### Added
- Modern Pythonic API with context manager support (`with UniversalSpeech() as speech:`).
- Object-oriented `Voice` and `ScreenReaderInfo` data models.
- Screen reader availability methods: `nvda_is_available()`, `jaws_is_available()`, `narrator_is_available()`, etc.
- Version lookup methods: `nvda_get_version()`, `jfw_get_version()`.
- Playback control: `is_busy`, `is_paused`, `pause()`, `resume()`, `wait()`, `say_ssml()`.
- Modern CLI interface via `python -m UniversalSpeech`.
- Strict typing, type hints, and `py.typed` marker.

### Changed
- Refactored project layout to standard PyPA layout with `pyproject.toml`.
- Deprecated low-level numeric constant getters and setters in favor of direct properties.

### Removed
- Removed legacy and unmaintained `ZDSRAPI.dll`.

---

## [1.0.0] - Prior Releases
- Initial Python ctypes wrapper around Quentin Cosendey's `UniversalSpeech.dll` for Windows 32-bit and 64-bit.
