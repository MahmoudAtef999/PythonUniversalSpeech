"""
UniversalSpeech Example Usage (Version 3.0.0)
"""
from UniversalSpeech import UniversalSpeech, UnsupportedError, VoiceError

# Using UniversalSpeech as a context manager
with UniversalSpeech() as speech:
    print(f"UniversalSpeech instance: {speech}")
    print(f"Active Engine:        {speech.engine_used}")
    print(f"Active Screen Reader: {speech.current_screen_reader_name}")

    # Check screen reader availability and versions
    print("\n--- Screen Reader Availability & Versions ---")
    nvda_ver = speech.nvda_get_version()
    jaws_ver = speech.jfw_get_version()
    print(f"NVDA available:      {speech.nvda_is_available()}" + (f" (Version: {nvda_ver})" if nvda_ver else ""))
    print(f"JAWS available:      {speech.jaws_is_available()}" + (f" (Version: {jaws_ver})" if jaws_ver else ""))
    print(f"Narrator available:  {speech.narrator_is_available()}")
    print(f"SAPI5 available:     {speech.sapi_is_available()}")

    # Voice discovery and selection
    if speech.voice_supported:
        voices = speech.get_voices()
        print(f"\nFound {len(voices)} available voices.")
        if voices:
            print(f"Default Voice: {speech.current_voice}")
            # Set to first voice
            speech.set_voice(voices[0])
            print(f"Selected Voice: {speech.current_voice}")

    # Speech and Braille output
    print("\nSpeaking and displaying braille...")
    speech.say("Hello from UniversalSpeech 3.0.0!", interrupt=True)
    speech.braille("UniversalSpeech 3.0.0")

    # Flow control: wait for speech to complete
    speech.wait(timeout_ms=1000)

    # Adjust speech rate if supported
    if speech.rate_supported:
        speech.set_rate(150)
        print("Rate set to 150.")

print("\nDone!")
