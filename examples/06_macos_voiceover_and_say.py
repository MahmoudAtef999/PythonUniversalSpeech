"""
Example 06: macOS VoiceOver & Native Speech
-------------------------------------------
Demonstrates macOS speech capabilities using Apple VoiceOver (AppleScript)
and native speech synthesis (/usr/bin/say) with voice discovery across languages.

Note: Run this on macOS.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    if sys.platform != "darwin":
        print(f"Notice: This example demonstrates macOS-specific speech features.")
        print(f"Current OS is '{sys.platform}'. Please run this on macOS.")
        return

    with UniversalSpeech() as speech:
        print("=== macOS VoiceOver & Native Speech Demo ===")
        print(f"Backend:              {speech.backend.__class__.__name__}")
        print(f"Current Engine:       {speech.engine_used}")

        # Check VoiceOver screen reader
        vo_active = speech.voiceover_is_available() if hasattr(speech, "voiceover_is_available") else False
        print(f"VoiceOver Running:    {vo_active}")

        # List discovered macOS voices and locales
        voices = speech.get_voices()
        print(f"\nDiscovered {len(voices)} macOS Voices:")
        for v in voices[:10]: # Print first 10
            lang_str = f" [{v.language}]" if v.language else ""
            print(f"  [{v.id}] {v.name}{lang_str}")
        if len(voices) > 10:
            print(f"  ... and {len(voices) - 10} more voices.")

        # Speak via active engine
        print("\nSpeaking greeting...")
        speech.say("Hello from UniversalSpeech on macOS!")
        speech.wait(timeout_ms=2500)

        # Select a specific voice by name if available (e.g., Samantha, Alex)
        for target_voice in ("Samantha", "Alex", "Tarik", "Maged"):
            try:
                speech.set_voice(target_voice)
                print(f"\nSelected voice '{target_voice}'. Current: {speech.current_voice}")
                speech.say(f"Speaking with voice {target_voice}.")
                speech.wait(timeout_ms=2500)
                break
            except Exception:
                continue


if __name__ == "__main__":
    main()
