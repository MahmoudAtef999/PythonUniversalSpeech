"""
Example 04: Windows Screen Readers & JAWS Scripting
---------------------------------------------------
Demonstrates checking Windows screen readers (NVDA, JAWS, Narrator, SuperNova),
reading active versions, executing JAWS scripts, and querying settings paths.

Note: Run this on Windows.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech, ScreenReaderId


def main():
    if sys.platform != "win32":
        print(f"Notice: This example demonstrates Windows-specific screen reader features.")
        print(f"Current OS is '{sys.platform}'. Please run this on Windows.")
        return

    with UniversalSpeech() as speech:
        print("=== Windows Screen Readers & Scripting Demo ===")

        # Check availability of individual screen readers
        print(f"NVDA running:       {speech.nvda_is_available()}" + (f" (Version {speech.nvda_get_version()})" if speech.nvda_is_available() else ""))
        print(f"JAWS running:       {speech.jaws_is_available()}" + (f" (Version {speech.jaws_get_version()})" if speech.jaws_is_available() else ""))
        print(f"Narrator running:   {speech.narrator_is_available()}")
        print(f"SuperNova running:  {speech.supernova_is_available()}")
        print(f"System Access:      {speech.system_access_is_available()}")
        print(f"SAPI5 available:    {speech.sapi_is_available()}")

        # JAWS Scripting and Settings Directory
        if speech.jaws_is_available():
            print("\n--- JAWS Advanced Scripting ---")
            jaws_settings = speech.jaws_get_user_settings_directory()
            print(f"JAWS User Settings Folder: {jaws_settings}")

            # Example: Running a built-in JAWS script (e.g. SayLine)
            print("Executing JAWS SayLine script...")
            success = speech.jaws_run_script("SayLine")
            print(f"Script execution result: {'Success' if success else 'Failed'}")
        else:
            print("\nJAWS is not currently running. To test JAWS scripting, launch JAWS first.")

        # Test speaking with active reader or SAPI5
        print("\nSpeaking announcement...")
        speech.say("UniversalSpeech Windows demo completed successfully.")
        speech.wait(timeout_ms=2000)


if __name__ == "__main__":
    main()
