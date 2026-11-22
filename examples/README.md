# UniversalSpeech Examples

This directory contains standalone, practical examples demonstrating various capabilities of **PythonUniversalSpeech v3.0**.

All examples can be executed directly with Python 3.7+ without any external dependencies.

---

## Example Index

| File | Description | Supported Platforms |
| :--- | :--- | :--- |
| [`01_quickstart_cross_platform.py`](01_quickstart_cross_platform.py) | Basic portable speech using context manager. | Windows, Linux, macOS |
| [`02_speech_parameters.py`](02_speech_parameters.py) | Adjusting speech rate, volume, and pitch using direct property access & ranges. | Windows, Linux, macOS |
| [`03_system_diagnostics.py`](03_system_diagnostics.py) | Querying structured diagnostics and printing formatted health reports. | Windows, Linux, macOS |
| [`04_windows_screen_readers_and_jaws.py`](04_windows_screen_readers_and_jaws.py) | Checking NVDA, JAWS, Narrator, executing JAWS scripts, and locating settings. | Windows |
| [`05_linux_speech_dispatcher_and_orca.py`](05_linux_speech_dispatcher_and_orca.py) | Speech Dispatcher (SSIP), eSpeak-ng, Orca screen reader query, engine switching. | Linux |
| [`06_macos_voiceover_and_say.py`](06_macos_voiceover_and_say.py) | Apple VoiceOver, native speech (`say`), and voice discovery across locales. | macOS |
| [`07_braille_display.py`](07_braille_display.py) | Refreshable braille display output and simultaneous speech + braille. | Windows, Linux |
| [`08_concurrency_and_threading.py`](08_concurrency_and_threading.py) | Thread-safe speech notifications from multiple concurrent background worker threads. | Windows, Linux, macOS |

---

## Running the Examples

Run any example directly from your terminal:

```bash
# Cross-Platform Quickstart
python examples/01_quickstart_cross_platform.py

# Speech Parameters & Ranges
python examples/02_speech_parameters.py

# System Diagnostics
python examples/03_system_diagnostics.py

# Windows Specific (NVDA, JAWS Scripting)
python examples/04_windows_screen_readers_and_jaws.py

# Linux Specific (Speech Dispatcher, Orca, eSpeak)
python examples/05_linux_speech_dispatcher_and_orca.py

# macOS Specific (VoiceOver, Native Voices)
python examples/06_macos_voiceover_and_say.py

# Braille Output
python examples/07_braille_display.py

# Threading & Concurrency
python examples/08_concurrency_and_threading.py
```
