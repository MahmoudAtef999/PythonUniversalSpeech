"""
Command-line interface (CLI) entry point for UniversalSpeech.

Usage:
    python -m UniversalSpeech "Text to speak"
    python -m UniversalSpeech --list-engines
    python -m UniversalSpeech --list-voices
    python -m UniversalSpeech --list-readers
    python -m UniversalSpeech --current
    python -m UniversalSpeech --version
"""
import sys
import argparse
from typing import Optional
from .core import UniversalSpeech
from . import __version__


def main(args: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m UniversalSpeech",
        description="UniversalSpeech CLI - Speak messages, list speech engines, voices, and screen readers.",
    )
    parser.add_argument(
        "message",
        nargs="?",
        default=None,
        help="Message to speak and/or display in braille.",
    )
    parser.add_argument(
        "-b", "--braille",
        action="store_true",
        help="Also output the message to connected braille display.",
    )
    parser.add_argument(
        "--no-interrupt",
        action="store_true",
        help="Do not interrupt ongoing speech.",
    )
    parser.add_argument(
        "-e", "--engine",
        type=str,
        help="Specify speech synthesis engine to use (e.g., SAPI5, NVDA, Jaws).",
    )
    parser.add_argument(
        "-v", "--voice",
        type=str,
        help="Specify voice name or index to use.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait until speech finishes before exiting.",
    )
    parser.add_argument(
        "--list-engines",
        action="store_true",
        help="List all supported engines and their availability.",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List all available voices for the current speech engine.",
    )
    parser.add_argument(
        "--list-readers",
        action="store_true",
        help="List all supported screen readers and their availability.",
    )
    parser.add_argument(
        "--current",
        action="store_true",
        help="Show current engine, active screen reader, and active voice.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"UniversalSpeech {__version__}",
    )

    parsed = parser.parse_args(args)

    with UniversalSpeech() as speech:
        if parsed.engine:
            speech.set_engine(parsed.engine)

        if parsed.voice:
            # Check if index or name
            if parsed.voice.isdigit():
                speech.set_voice(int(parsed.voice))
            else:
                speech.set_voice(parsed.voice)

        if parsed.list_engines:
            print("Supported Speech Engines:")
            for name, details in speech.get_engines().items():
                status = "[Available]" if details["available"] else "[Unavailable]"
                print(f"  - {name:<16} {status}")
            return 0

        if parsed.list_voices:
            voices = speech.get_voices()
            if not voices:
                print(f"No voices available for engine '{speech.engine_used}'.")
            else:
                print(f"Available Voices for '{speech.engine_used}':")
                for v in voices:
                    print(f"  [{v.id}] {v.name}")
            return 0

        if parsed.list_readers:
            print("Supported Screen Readers:")
            for r in speech.get_screen_readers():
                status = "[Active/Running]" if r.available else "[Not Detected]"
                print(f"  - {r.name:<16} {status}")
            return 0

        if parsed.current:
            cur_voice = speech.get_voice()
            voice_str = cur_voice.name if cur_voice else "N/A"
            print(f"Active Engine:        {speech.engine_used}")
            print(f"Active Screen Reader: {speech.current_screen_reader_name or 'None'}")
            print(f"Current Voice:        {voice_str}")
            return 0

        if parsed.message:
            interrupt = not parsed.no_interrupt
            if parsed.braille:
                speech.speech(parsed.message)
            else:
                speech.say(parsed.message, interrupt=interrupt)
            if parsed.wait:
                speech.wait()
            return 0

        # If no action specified, print help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
