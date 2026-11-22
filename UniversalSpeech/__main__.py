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
        "-d", "--diagnostics",
        action="store_true",
        help="Show comprehensive system and speech engine diagnostics report.",
    )
    parser.add_argument(
        "--rate",
        type=int,
        help="Set speech rate (if supported by active engine).",
    )
    parser.add_argument(
        "--volume",
        type=int,
        help="Set speech volume (if supported by active engine).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"UniversalSpeech {__version__}",
    )

    parsed = parser.parse_args(args)

    with UniversalSpeech(stop_on_exit=False) as speech:
        if parsed.engine:
            speech.set_engine(parsed.engine)

        if parsed.voice:
            # Check if index or name
            if parsed.voice.isdigit():
                speech.set_voice(int(parsed.voice))
            else:
                speech.set_voice(parsed.voice)

        if parsed.rate is not None:
            if speech.rate_supported:
                speech.rate = parsed.rate
            else:
                print(f"Warning: Speech rate control is not supported by engine '{speech.engine_used}'.", file=sys.stderr)

        if parsed.volume is not None:
            if speech.volume_supported:
                speech.volume = parsed.volume
            else:
                print(f"Warning: Speech volume control is not supported by engine '{speech.engine_used}'.", file=sys.stderr)

        if parsed.diagnostics:
            print(speech.diagnostics_summary())
            return 0

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
                ver = None
                if "nvda" in r.name.lower():
                    ver = speech.nvda_get_version()
                elif "jaws" in r.name.lower() or "jfw" in r.name.lower():
                    ver = speech.jfw_get_version()
                ver_suffix = f" (v{ver})" if ver else ""
                status = f"[Active/Running{ver_suffix}]" if r.available else (f"[Detected{ver_suffix}]" if ver else "[Not Detected]")
                print(f"  - {r.name:<16} {status}")
            return 0

        if parsed.current:
            cur_voice = speech.get_voice()
            voice_str = cur_voice.name if cur_voice else "N/A"
            print(f"Active Engine:        {speech.engine_used}")
            print(f"Active Screen Reader: {speech.current_screen_reader_name or 'None'}")
            print(f"Current Voice:        {voice_str}")
            return 0

        # Read from piped stdin if no message argument was provided
        if not parsed.message and sys.stdin is not None:
            try:
                is_pipe = False
                try:
                    is_pipe = not sys.stdin.isatty()
                except Exception:
                    is_pipe = False

                if is_pipe:
                    has_data = False
                    if sys.platform == "win32":
                        try:
                            import msvcrt
                            # Check if standard input has keyboard or pipe data ready
                            # PeekNamedPipe checks if there is data on pipe without blocking
                            import ctypes
                            from ctypes import wintypes
                            kernel32 = ctypes.windll.kernel32
                            STD_INPUT_HANDLE = -10
                            h_stdin = kernel32.GetStdHandle(STD_INPUT_HANDLE)
                            avail = wintypes.DWORD(0)
                            if kernel32.PeekNamedPipe(h_stdin, None, 0, None, ctypes.byref(avail), None):
                                has_data = avail.value > 0
                            elif hasattr(sys.stdin, "tell"):
                                # Fallback for StringIO / custom mocks in tests
                                has_data = True
                        except Exception:
                            has_data = True
                    else:
                        try:
                            import select
                            r, _, _ = select.select([sys.stdin], [], [], 0.0)
                            has_data = bool(r)
                        except Exception:
                            has_data = True

                    if has_data:
                        piped_msg = sys.stdin.read().strip()
                        if piped_msg:
                            parsed.message = piped_msg
            except Exception:
                pass

        if parsed.message:
            interrupt = not parsed.no_interrupt
            if parsed.braille:
                speech.speech(parsed.message)
            else:
                speech.say(parsed.message, interrupt=interrupt)

            # Auto-wait if explicitly requested, or for in-process engines (like SAPI)
            # where process termination immediately kills audio before it is heard.
            engine_name = speech.engine_used.lower()
            if parsed.wait or "sapi" in engine_name:
                speech.wait()
            return 0

        # If no action specified, print help
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
