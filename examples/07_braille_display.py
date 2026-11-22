"""
Example 07: Braille Display & Simultaneous Output
-------------------------------------------------
Demonstrates displaying text on connected refreshable braille displays
or sending simultaneous speech and braille output.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    print("=== Braille Display & Speech Output Demo ===")

    with UniversalSpeech() as speech:
        # 1. Output purely to braille display
        print("Sending message to Braille display...")
        speech.braille("Braille: Status Normal")

        # 2. Output simultaneously to both speech synthesis and braille display
        print("Sending simultaneous speech and braille announcement...")
        speech.speech("Alert: Download completed successfully.", interrupt=True)

        if speech.wait_supported:
            speech.wait(timeout_ms=2500)

    print("Completed!")


if __name__ == "__main__":
    main()
