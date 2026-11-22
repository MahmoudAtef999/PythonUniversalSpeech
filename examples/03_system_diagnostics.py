"""
Example 03: System Diagnostics & Health Check
---------------------------------------------
Demonstrates querying deep environment diagnostics to inspect detected screen
readers, engines, voices, and capability flags.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    with UniversalSpeech() as speech:
        # 1. Print structured dictionary diagnostics
        diag = speech.get_diagnostics()
        print("=== Structured Diagnostics Dictionary ===")
        print(f"Host Platform:          {diag['platform']}")
        print(f"Backend Class:          {diag.get('backend', 'N/A')}")
        print(f"Active Speech Engine:   {diag['engine_used']}")
        print(f"Active Screen Reader:   {diag['active_screen_reader_name']} (ID: {diag['active_screen_reader_id']})")
        print(f"Available Voices Count: {diag['voices_count']}")

        print("\nSupported Engines:")
        for name, info in diag["engines"].items():
            status = "Available" if info["available"] else "Not available"
            print(f"  - {name:<18}: {status}")

        print("\n--- Formatted Diagnostics Summary Report ---")
        # 2. Print the human-readable summary
        print(speech.diagnostics_summary())


if __name__ == "__main__":
    main()
