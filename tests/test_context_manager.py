"""
Unit tests for context manager, resource cleanup, and string representation.
"""
import unittest
from UniversalSpeech import UniversalSpeech


class TestContextManager(unittest.TestCase):
    def test_context_manager_usage(self):
        with UniversalSpeech() as speech:
            self.assertIsInstance(speech, UniversalSpeech)
            speech.say("Context manager test")
            speech.stop()

    def test_close_method(self):
        speech = UniversalSpeech()
        speech.say("Close method test")
        speech.close()

    def test_repr_and_str(self):
        speech = UniversalSpeech()
        r = repr(speech)
        s = str(speech)
        self.assertTrue(r.startswith("<UniversalSpeech"))
        self.assertTrue(s.startswith("UniversalSpeech("))
        self.assertIn("engine=", r)


if __name__ == "__main__":
    unittest.main()
