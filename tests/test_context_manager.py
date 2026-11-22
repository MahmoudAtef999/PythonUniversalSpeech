"""
Unit tests for context manager, resource cleanup, and string representation.
"""
import copy
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

    def test_copy_and_getattr_no_recursion(self):
        speech = UniversalSpeech()
        # Verify copy.copy does not raise RecursionError
        copied = copy.copy(speech)
        self.assertIsInstance(copied, UniversalSpeech)

        # Verify accessing non-existent private attribute raises AttributeError without recursion
        with self.assertRaises(AttributeError):
            _ = speech._non_existent

        # Verify an instance without _backend raises AttributeError without recursion
        uninitialized = UniversalSpeech.__new__(UniversalSpeech)
        with self.assertRaises(AttributeError):
            _ = uninitialized.any_attribute


if __name__ == "__main__":
    unittest.main()
