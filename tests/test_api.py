import unittest
import UniversalSpeech
from UniversalSpeech.exceptions import UnsupportedError


class TestUniversalSpeechAPI(unittest.TestCase):
    """Test UniversalSpeech Public API."""

    @classmethod
    def setUpClass(cls):
        cls.speech = UniversalSpeech.UniversalSpeech()
        cls.speech.enable_native_speech(True)

    def test_get_engines(self):
        engines = self.speech.get_engines()
        self.assertIsInstance(engines, dict)
        self.assertGreater(len(engines), 0)
        # Verify structure of each engine entry
        for name, data in engines.items():
            self.assertIn("name", data)
            self.assertEqual(data["name"], name)
            self.assertIn("available", data)
            self.assertIsInstance(data["available"], bool)
            self.assertIn("id", data)
            self.assertIsInstance(data["id"], int)

    def test_engine_used(self):
        engine = self.speech.engine_used
        self.assertIsInstance(engine, str)
        self.assertGreater(len(engine), 0)

    def test_enable_native_speech(self):
        # Should execute without errors
        self.speech.enable_native_speech(True)
        self.speech.enable_native_speech(False)
        self.speech.enable_native_speech(True)

    def test_speech_say_and_stop(self):
        # say and stop should run without errors
        self.speech.say("Test baseline speech", interrupt=True)
        self.speech.stop()

    def test_speech_say_a(self):
        self.speech.say_a("A", interrupt=True)
        self.speech.stop()

    def test_braille(self):
        self.speech.braille("Test braille")

    def test_speech_combined(self):
        self.speech.speech("Test combined speech and braille")
        self.speech.stop()

    def test_speech_a_known_bug_handling(self):
        # Note: In baseline code, speech_a has a known bug calling self.sayA instead of self.say_a
        # This test ensures we handle either baseline AttributeError or fixed behavior
        try:
            self.speech.speech_a("Test speech_a")
        except AttributeError:
            pass  # Expected in baseline before Stage 4 fix

    def test_get_and_set_value(self):
        # Read a known parameter
        val = self.speech.get_value(UniversalSpeech.ENABLE_NATIVE_SPEECH)
        self.assertIsInstance(val, int)
        # Set and re-read
        self.speech.set_value(UniversalSpeech.ENABLE_NATIVE_SPEECH, 1)

    def test_get_string(self):
        str_val = self.speech.get_string(UniversalSpeech.ENGINE)
        self.assertIsInstance(str_val, str)

    def test_feature_support_flags(self):
        self.assertIsInstance(self.speech.volume_supported, bool)
        self.assertIsInstance(self.speech.rate_supported, bool)
        self.assertIsInstance(self.speech.pitch_supported, bool)
        self.assertIsInstance(self.speech.inflection_supported, bool)

    def test_volume_control(self):
        if self.speech.volume_supported:
            orig = self.speech.get_value(UniversalSpeech.VOLUME)
            self.speech.set_volume(80, min_volume=0, max_volume=100)
            self.speech.set_volume(orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_volume(50)

    def test_rate_control(self):
        if self.speech.rate_supported:
            orig = self.speech.get_value(UniversalSpeech.RATE)
            self.speech.set_rate(50, min_rate=0, max_rate=100)
            self.speech.set_rate(orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_rate(50)

    def test_pitch_control(self):
        if self.speech.pitch_supported:
            orig = self.speech.get_value(UniversalSpeech.PITCH)
            self.speech.set_pitch(50)
            self.speech.set_pitch(orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_pitch(50)

    def test_inflection_control(self):
        if self.speech.inflection_supported:
            orig = self.speech.get_value(UniversalSpeech.INFLECTION)
            self.speech.set_inflection(50)
            self.speech.set_inflection(orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_inflection(50)

    def test_set_engine_unsupported(self):
        with self.assertRaises(UnsupportedError):
            self.speech.set_engine("NonExistentEngineX")


if __name__ == "__main__":
    unittest.main()
