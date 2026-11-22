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

    def test_stop_on_exit_default_and_custom(self):
        # Default should be False so speech is not cut off
        speech = UniversalSpeech()
        self.assertFalse(speech.stop_on_exit)

        speech.stop_on_exit = True
        self.assertTrue(speech.stop_on_exit)

        with UniversalSpeech(stop_on_exit=True) as s:
            self.assertTrue(s.stop_on_exit)

        with UniversalSpeech(stop_on_exit=False) as s:
            self.assertFalse(s.stop_on_exit)

    def test_repr_and_str(self):
        speech = UniversalSpeech()
        r = repr(speech)
        s = str(speech)
        self.assertTrue(r.startswith("<UniversalSpeech"))
        self.assertTrue(s.startswith("UniversalSpeech("))
        self.assertIn("engine=", r)


if __name__ == "__main__":
    unittest.main()
