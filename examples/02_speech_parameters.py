"""
Example 02: Pythonic Speech Parameters & Bounds
----------------------------------------------
Demonstrates inspecting parameter support, querying min/max bounds,
and adjusting rate, volume, and pitch using direct property access.
"""
import sys
import os

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def main():
    with UniversalSpeech() as speech:
        print("=== Speech Parameters Inspection & Control ===")
        print(f"Engine: {speech.engine_used}")

        # --- Rate (Speed) ---
        if speech.rate_supported:
            min_r, max_r = speech.rate_range
            print(f"\n[Rate] Supported: Min={min_r}, Max={max_r}, Current={speech.rate}")
            # Speed up slightly
            speech.rate = min(max_r, speech.rate + 20)
            print(f"New rate set to: {speech.rate}")
            speech.say("Speaking at a faster rate.")
            if speech.wait_supported:
                speech.wait(timeout_ms=2000)
        else:
            print("\n[Rate] Not supported by current engine.")

        # --- Volume ---
        if speech.volume_supported:
            min_v, max_v = speech.volume_range
            print(f"\n[Volume] Supported: Min={min_v}, Max={max_v}, Current={speech.volume}")
            # Set volume to 80%
            speech.volume = 80
            print(f"Volume adjusted to: {speech.volume}")
            speech.say("Speaking at volume 80 percent.")
            if speech.wait_supported:
                speech.wait(timeout_ms=2000)
        else:
            print("\n[Volume] Not supported by current engine.")

        # --- Pitch ---
        if speech.pitch_supported:
            min_p, max_p = speech.pitch_range
            print(f"\n[Pitch] Supported: Min={min_p}, Max={max_p}, Current={speech.pitch}")
            speech.pitch = 70
            print(f"Pitch adjusted to: {speech.pitch}")
            speech.say("Speaking with higher pitch.")
            if speech.wait_supported:
                speech.wait(timeout_ms=2000)
        else:
            print("\n[Pitch] Not supported by current engine.")


if __name__ == "__main__":
    main()
