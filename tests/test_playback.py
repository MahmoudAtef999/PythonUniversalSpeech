"""
Unit tests for playback and flow control methods in UniversalSpeech.
"""
import sys
import unittest
from UniversalSpeech import UniversalSpeech, UnsupportedError


@unittest.skipUnless(sys.platform == "win32", "Windows playback control tests require Windows DLL")
class TestPlaybackControl(unittest.TestCase):
    def setUp(self):
        self.speech = UniversalSpeech()

    def test_reset_engine(self):
        # Setting engine then resetting
        engines = self.speech.get_engines()
        if engines:
            first_engine = next(iter(engines.keys()))
            self.speech.set_engine(first_engine)
        self.speech.reset_engine()
        # Engine should still be usable
        self.assertTrue(len(self.speech.engine_used) > 0)

    def test_is_busy_and_busy_supported(self):
        self.assertIsInstance(self.speech.busy_supported, bool)
        self.assertIsInstance(self.speech.is_busy, bool)

    def test_is_paused_and_pause_supported(self):
        self.assertIsInstance(self.speech.pause_supported, bool)
        self.assertIsInstance(self.speech.is_paused, bool)

    def test_pause_and_resume(self):
        if self.speech.pause_supported:
            # Test that pause and resume methods execute cleanly
            self.speech.pause(True)
            self.assertIsInstance(self.speech.is_paused, bool)
            self.speech.resume()
            self.assertIsInstance(self.speech.is_paused, bool)

    def test_wait_and_wait_supported(self):
        self.assertIsInstance(self.speech.wait_supported, bool)
        # Calling wait when idle should return True if supported or False if unsupported
        res = self.speech.wait(timeout_ms=10)
        self.assertIsInstance(res, bool)

    def test_wait_reflects_busy_status(self):
        engines = self.speech.get_engines()
        if "SAPI5" in engines:
            self.speech.set_engine("SAPI5")
        if self.speech.busy_supported:
            self.speech.stop()
            # When not busy, wait should return True
            self.assertTrue(self.speech.wait(timeout_ms=100))

            # When speaking a longer text, test wait behavior
            self.speech.say("This is a longer sentence to test timeout and busy status checking in wait.")
            # If still busy, a tiny timeout (1ms) should return False when busy checking is active
            if self.speech.is_busy:
                res = self.speech.wait(timeout_ms=1)
                self.assertFalse(res)
            self.speech.stop()

    def test_say_ssml(self):
        # Plain text in say_ssml is supported by SAPI XML engine
        res = self.speech.say_ssml("Testing SSML speech")
        self.assertIsInstance(res, bool)
        self.speech.stop()


if __name__ == "__main__":
    unittest.main()
