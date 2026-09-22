"""
Comprehensive demonstration of UniversalSpeech 2.0.0 features with SAPI5.
All messages, logs, and outputs are presented entirely in English.
"""
import time
from UniversalSpeech import UniversalSpeech, VoiceError, UnsupportedError


def main() -> None:
    print("==================================================")
    print("    UniversalSpeech 2.0.0 Feature Demo (SAPI5)   ")
    print("==================================================\n")

    # 1. Using Context Manager
    with UniversalSpeech() as speech:
        print(f"1. Initialized instance: {speech}")

        # 2. Select SAPI5 engine explicitly and enable native engines
        speech.enable_native_speech(True)
        speech.set_engine("SAPI5")
        print(f"2. Active Engine:        {speech.engine_used}")
        print(f"   Detected Screen Reader Name: {speech.current_screen_reader_name or 'None'}")
        print(f"   Screen Reader ID:            {speech.current_screen_reader_id}")

        # 3. Check screen reader and engine availability
        print("\n--- 3. Screen Reader & Engine Availability ---")
        print(f"   Is SAPI5 available?     {speech.sapi_is_available()}")
        print(f"   Is NVDA running?        {speech.nvda_is_available()}")
        print(f"   Is JAWS running?        {speech.jaws_is_available()}")
        print(f"   Is Narrator running?    {speech.narrator_is_available()}")

        print("\n   All 10 supported screen readers and their status:")
        for reader in speech.get_screen_readers():
            status = "Active / Running" if reader.available else "Not Detected"
            print(f"     - [{reader.id}] {reader.name:<16}: {status}")

        # 4. Voice discovery and management
        print("\n--- 4. Voice Discovery & Management (SAPI5) ---")
        print(f"   Are voices supported? {speech.voice_supported}")
        voices = speech.get_voices()
        print(f"   Installed voices count: {len(voices)}")

        for v in voices:
            print(f"     [{v.id}] {v.name}")

        default_voice = speech.get_voice()
        print(f"   Default active voice: {default_voice}")

        # 5. Basic speech output and completion waiting
        print("\n--- 5. Speech Output and Synchronization (wait) ---")
        print("   Speaking greeting message...")
        speech.say("Hello! This is a complete demonstration of UniversalSpeech 2.0.0 with SAPI5.")
        speech.wait()
        print("   Speech completed.")

        # 6. Character-by-character speech (say_a)
        print("\n--- 6. Character Output (say_a) ---")
        for char in ["A", "B", "C"]:
            print(f"   Speaking letter: {char}")
            speech.say_a(char)
            speech.wait()

        # 7. Volume and speech rate control
        print("\n--- 7. Volume and Rate Control ---")
        if speech.volume_supported:
            print("   Lowering volume to 60%...")
            speech.set_volume(60)
            speech.say("Volume is now set to 60 percent.")
            speech.wait()
            # Restore volume
            speech.set_volume(100)

        if speech.rate_supported:
            print("   Increasing speech rate to 200...")
            speech.set_rate(200)
            speech.say("This is fast speech at rate 200.")
            speech.wait()
            print("   Restoring speech rate to normal (100)...")
            speech.set_rate(100)
            speech.say("Speech rate is back to normal.")
            speech.wait()

        # 8. Switching voices (by substring or index)
        if len(voices) > 1:
            print("\n--- 8. Voice Switching by Name / Substring ---")
            # Try switching by partial name "Zira" or second voice
            target_voice = "Zira" if any("zira" in v.name.lower() for v in voices) else voices[1].name
            print(f"   Switching to voice matching '{target_voice}'...")
            try:
                speech.set_voice(target_voice)
                print(f"   Current voice after switch: {speech.current_voice}")
                speech.say(f"Voice switched successfully to {speech.current_voice.name}.")
                speech.wait()
            except VoiceError as err:
                print(f"   Voice switch error: {err}")

            # Revert to default voice (index 0)
            speech.set_voice(0)
            print(f"   Reverted to original voice: {speech.current_voice}")

        # 9. Checking busy state (is_busy)
        print("\n--- 9. Checking Busy State (is_busy) ---")
        print(f"   Is busy before speech? {speech.is_busy}")
        speech.say("This is a longer sentence to test speech busy state detection.")
        time.sleep(0.05)
        print(f"   Is busy during speech? {speech.is_busy}")
        speech.wait()
        print(f"   Is busy after speech?  {speech.is_busy}")

        # 10. SSML / XML speech
        print("\n--- 10. SSML / XML Output ---")
        speech.say_ssml("Testing SSML speech markup with SAPI engine.")
        speech.wait()

        # 11. Restore automatic engine detection
        print("\n--- 11. Restoring Automatic Engine Detection (reset_engine) ---")
        speech.reset_engine()
        print(f"   Engine after reset_engine(): {speech.engine_used}")

    print("\n==================================================")
    print("    All tests completed successfully!            ")
    print("==================================================")


if __name__ == "__main__":
    main()
