"""
Unit tests for UniversalSpeech CLI (__main__.py).
"""
import io
import sys
import unittest
from UniversalSpeech.__main__ import main


class TestCLI(unittest.TestCase):
    def test_cli_current(self):
        buf = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.stdout = buf
            ret = main(["--current"])
            self.assertEqual(ret, 0)
            output = buf.getvalue()
            self.assertIn("Active Engine:", output)
            self.assertIn("Active Screen Reader:", output)
        finally:
            sys.stdout = orig_stdout

    def test_cli_list_engines(self):
        buf = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.stdout = buf
            ret = main(["--list-engines"])
            self.assertEqual(ret, 0)
            output = buf.getvalue()
            self.assertIn("Supported Speech Engines:", output)
        finally:
            sys.stdout = orig_stdout

    def test_cli_list_readers(self):
        buf = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.stdout = buf
            ret = main(["--list-readers"])
            self.assertEqual(ret, 0)
            output = buf.getvalue()
            self.assertIn("Supported Screen Readers:", output)
        finally:
            sys.stdout = orig_stdout

    def test_cli_list_voices(self):
        buf = io.StringIO()
        orig_stdout = sys.stdout
        try:
            sys.stdout = buf
            ret = main(["--list-voices"])
            self.assertEqual(ret, 0)
        finally:
            sys.stdout = orig_stdout

    def test_cli_message_speak(self):
        ret = main(["Testing CLI speech message", "--wait"])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
