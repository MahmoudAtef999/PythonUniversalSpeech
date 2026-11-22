"""
Example 05: Linux Speech Dispatcher & Orca
------------------------------------------
Demonstrates Linux speech capabilities using Speech Dispatcher (SSIP socket / spd-say),
eSpeak-ng, and querying Orca screen reader status.

Note: Run this on Linux.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    if not sys.platform.startswith("linux"):
        print(f"Notice: This example demonstrates Linux-specific speech features.")
        print(f"Current OS is '{sys.platform}'. Please run this on Linux.")
        return

    with UniversalSpeech() as speech:
        print("=== Linux Speech & Orca Demo ===")
        print(f"Backend:              {speech.backend.__class__.__name__}")
        print(f"Current Engine:       {speech.engine_used}")

        # Orca screen reader detection
        orca_active = speech.orca_is_available() if hasattr(speech, "orca_is_available") else False
        orca_ver = speech.orca_get_version() if hasattr(speech, "orca_get_version") else None
        print(f"Orca Running:         {orca_active}" + (f" (Version: {orca_ver})" if orca_ver else ""))

        # Available Linux Engines
        engines = speech.get_engines()
        print("\nAvailable Engines:")
        for name, details in engines.items():
            print(f"  [{details['id']}] {details['name']}: {'Available' if details['available'] else 'Unavailable'}")

        # Speak using default active engine (Speech Dispatcher or eSpeak)
        print("\nSpeaking message via Linux active engine...")
        speech.say("Hello from UniversalSpeech on Linux!")
        speech.wait(timeout_ms=2500)

        # Explicitly switch engine if eSpeak is available
        if "espeak" in engines and engines["espeak"]["available"]:
            print("\nSwitching active engine to eSpeak...")
            speech.set_engine("espeak")
            print(f"Engine is now: {speech.engine_used}")
            speech.say("This message is spoken directly by eSpeak.")
            speech.wait(timeout_ms=2500)

        # Restore default auto selection
        speech.reset_engine()


if __name__ == "__main__":
    main()
