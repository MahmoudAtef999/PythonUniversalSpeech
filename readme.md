# PythonUniversalSpeech

## Overview:

The PythonUniversalSpeech library is a Python interface for interacting with the UniversalSpeech DLL, providing convenient functionality for speech synthesis and braille display. This library is compatible with both 32-bit and 64-bit versions of Python.

UniversalSpeech aims to streamline and simplify access to speech within applications. It accomplishes this by providing a unified interface that allows speech to be achieved through various means, including active screen readers, direct synthesis, or native/OS speech engines. The library dynamically adapts based on what is available and supported, offering a cohesive and versatile solution for speech-related functionalities.

PythonUniversalSpeech is built upon the UniversalSpeech, initially developed by [qtnc](https://github.com/qtnc). To learn more about the project and its details, you can visit the [UniversalSpeech GitHub repository](https://github.com/qtnc/UniversalSpeech).

## Supported engines:

- Jaws for windows.
- NVDA 2011.1 or above.
- Windows eye.
- System access.
- Supernova.
- Cobra, partially.
- SAPI 5.
- ZDSRAPI

## Installation:

To install the UniversalSpeech library, you can use the following pip command:

```bash
pip install UniversalSpeech
```

Alternatively, you can download the project directly from the GitHub repository here and use it in your Python project.

## Usage:

### UniversalSpeech Class:

The `UniversalSpeech` class provides a simplified interface for workingwith the UniversalSpeech DLL.

### Attributes:

- `engine_used` (str): Returns the name of the currently used speech engine.
- `rate_supported` (bool): Indicates whether setting the speech rate is supported in the current engine.
- `volume_supported` (bool): Indicates whether setting the speech volume is supported in the current engine.
- `pitch_supported` (bool): Indicates whether setting the speech pitch is supported in the current engine.
- `inflection_supported` (bool): Indicates whether setting the speech inflection is supported in the current engine.

### Methods:

- `say(msg: str, interrupt: bool = True) -> None`: 
  - Says the given message using the speech engine.

- `say_a(msg: str, interrupt: bool = True) -> None`: 
  - Says the first letter of the given message using the speech engine.

- `braille(msg: str) -> None`: 
  - Displays the given message in braille.

- `speech(msg: str) -> None`: 
  - Performs both speech and braille display for the given message.

- `speech_a(msg: str) -> None`: 
  - Performs  speech_a and braille  for the given message.

- `stop() -> None`: 
  - Stops the speech.

- `get_value(what) -> int`: 
  - Gets the current value of a specific speech parameter.
  - Note: You can see the available parameters by looking at the beginning of [this file](https://github.com/MahmoudAtef999/PythonUniversalSpeech/blob/main/UniversalSpeech/__init__.py).

- `set_value(what, value) -> None`: 
  - Sets the value of a specific speech parameter.

- `get_string(what) -> str`: 
  - Gets a string representation of a specific speech parameter.

- `enable_native_speech(enabled: bool = True) -> None`: 
  - Determines whether to use native speech engines, such as SAPI on Windows, that are generally reliable and can be used when no other engines are available. 
  - If enabled is set to True, native speech engines are used; if set to False, speech is ignored in such cases.

- `get_engines() -> List[Dict]`: 
  - Gets a list of available speech engines with their names, availability, and IDs.

- `set_rate(value: int, min_rate: int = None, max_rate: int = None) -> None`: 
  - Sets the speech rate and, optionally, the minimum and maximum rates.

- `set_volume(value: int, min_volume: int = None, max_volume: int = None) -> None`: 
  - Sets the speech volume and, optionally, the minimum and maximum volume.

- `set_pitch(value: int, min_pitch: int = None, max_pitch: int = None) -> None`: 
  - Sets the speech pitch and, optionally, the minimum and maximum pitch.

- `set_inflection(value: int, min_inflexion: int = None, max_inflexion: int = None) -> None`: 
  - Sets the speech inflection and, optionally, the minimum and maximum inflexion.

## Exceptions:

- `DLLFileNotFoundError(Exception)`: 
  - Raised when one or more required DLL files are missing.

- `UnsupportedError(Exception)`: 
  - Raised when a specific function is not supported with the current engine.

## Example:

```python
import UniversalSpeech

# Create an instance of UniversalSpeech
uspeech = UniversalSpeech.UniversalSpeech()

# Enable the use of native speech engines such as SAPI 
uspeech.enable_native_speech(True)

#Say a message
uspeech.say("Hello, world.")

# Display a message in braille
uspeech.braille("Hello, world.")

# Get engine used
engine_used = uspeech.engine_used
print("You are using {}.".format(engine_used))

# Get list of available engins
available_engines = uspeech.get_engines()
print(available_engines)

# set the rate if it is supported
try:
    uspeech.set_rate(150)
except UniversalSpeech.exceptions.UnsupportedError as e:
    print(e)
```
