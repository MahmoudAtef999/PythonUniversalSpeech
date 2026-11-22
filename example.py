"""
UniversalSpeech Example Usage (Version 3.0.0-dev)
"""
from UniversalSpeech import UniversalSpeech, ScreenReaderId, UnsupportedError, VoiceError

# Using UniversalSpeech as a context manager
with UniversalSpeech() as speech:
    print(f"UniversalSpeech instance: {speech}")
    print(f"Active Engine:        {speech.engine_used}")
    print(f"Active Screen Reader: {speech.current_screen_reader_name}")

    # Check screen reader availability, versions, and JAWS scripting
    print("\n--- Screen Reader Availability & Versions ---")
    nvda_ver = speech.nvda_get_version()
    jaws_ver = speech.jfw_get_version()
    print(f"NVDA available:      {speech.nvda_is_available()}" + (f" (Version: {nvda_ver})" if nvda_ver else ""))
    print(f"JAWS available:      {speech.jaws_is_available()}" + (f" (Version: {jaws_ver})" if jaws_ver else ""))
    print(f"Narrator available:  {speech.narrator_is_available()}")
    print(f"SAPI5 available:     {speech.sapi_is_available()}")
    print(f"ZDSR available:      {speech.zdsr_is_available()}")

    if speech.jaws_is_available():
        jaws_dir = speech.jaws_get_user_settings_directory()
        print(f"JAWS settings dir:   {jaws_dir}")

    # Voice discovery and selection
    if speech.voice_supported:
        voices = speech.get_voices()
        print(f"\nFound {len(voices)} available voices.")
        if voices:
            print(f"Default Voice: {speech.current_voice}")
            # Set to first voice
            speech.set_voice(voices[0])
            print(f"Selected Voice: {speech.current_voice}")

    # Speech volume and rate using Pythonic property access & ranges
    if speech.volume_supported:
        print(f"\nVolume range: {speech.volume_range}")
        speech.volume = 90
        print(f"Current volume set via property: {speech.volume}")

    if speech.rate_supported:
        print(f"Rate range: {speech.rate_range}")
        speech.rate = 120
        print(f"Current rate set via property: {speech.rate}")

    # Speech and Braille output (with interrupt support)
    print("\nSpeaking and displaying braille...")
    speech.speech("Hello from UniversalSpeech!", interrupt=True)

    # Flow control: wait for speech to complete
    speech.wait(timeout_ms=1000)

    # Print diagnostics summary report
    print("\n--- Diagnostics Summary ---")
    print(speech.diagnostics_summary())

print("\nDone!")
