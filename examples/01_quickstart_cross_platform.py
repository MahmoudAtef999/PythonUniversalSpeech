"""
Example 01: Cross-Platform Quickstart
-------------------------------------
Demonstrates the most straightforward, portable way to use UniversalSpeech
across Windows, Linux, and macOS using a context manager.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    print("Initializing UniversalSpeech...")

    # Using UniversalSpeech as a context manager ensures all resources
    # and ongoing speech processes are properly cleaned up upon exit.
    with UniversalSpeech() as speech:
        print(f"Platform:             {speech.backend.__class__.__name__}")
        print(f"Active Engine:        {speech.engine_used}")
        print(f"Active Screen Reader: {speech.current_screen_reader_name or 'None'}")

        # Speak a message
        print("\nSpeaking message...")
        speech.say("Hello! UniversalSpeech is running successfully.")

        # Wait for speech playback to finish before exiting
        if speech.wait_supported:
            speech.wait(timeout_ms=3000)

    print("Completed!")


if __name__ == "__main__":
    main()
