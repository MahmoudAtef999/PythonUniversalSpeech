import unittest
import UniversalSpeech
from UniversalSpeech.exceptions import UnsupportedError, EngineError
from UniversalSpeech.constants import ScreenReaderId


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

    def test_speech_sayA_alias(self):
        # Test backward-compatible sayA alias
        self.speech.sayA("A", interrupt=True)
        self.speech.stop()

    def test_braille(self):
        self.speech.braille("Test braille")

    def test_speech_combined(self):
        self.speech.speech("Test combined speech and braille", interrupt=True)
        self.speech.speech("Test combined without interrupt", interrupt=False)
        self.speech.stop()

    def test_speech_a_method(self):
        # speech_a should execute say_a and braille without AttributeError
        self.speech.speech_a("Test speech_a", interrupt=True)
        self.speech.speech_a("Test speech_a non-interrupt", interrupt=False)
        self.speech.stop()

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
            orig = self.speech.get_volume()
            self.assertEqual(orig, self.speech.volume)
            self.assertIsInstance(self.speech.volume_min, int)
            self.assertIsInstance(self.speech.volume_max, int)
            self.speech.set_volume(80, min_volume=0, max_volume=100)
            self.assertEqual(self.speech.get_volume(), 80)
            self.speech.volume = orig
            self.assertEqual(self.speech.volume, orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_volume(50)
            with self.assertRaises(UnsupportedError):
                self.speech.get_volume()

    def test_rate_control(self):
        if self.speech.rate_supported:
            orig = self.speech.get_rate()
            self.assertEqual(orig, self.speech.rate)
            self.assertIsInstance(self.speech.rate_min, int)
            self.assertIsInstance(self.speech.rate_max, int)
            self.speech.set_rate(50, min_rate=0, max_rate=100)
            self.assertEqual(self.speech.get_rate(), 50)
            self.speech.rate = orig
            self.assertEqual(self.speech.rate, orig)
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_rate(50)
            with self.assertRaises(UnsupportedError):
                self.speech.get_rate()

    def test_pitch_control(self):
        if self.speech.pitch_supported:
            orig = self.speech.get_pitch()
            self.assertEqual(orig, self.speech.pitch)
            self.assertIsInstance(self.speech.pitch_min, int)
            self.assertIsInstance(self.speech.pitch_max, int)
            self.speech.set_pitch(50)
            self.speech.pitch = orig
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_pitch(50)
            with self.assertRaises(UnsupportedError):
                self.speech.get_pitch()

    def test_inflection_control(self):
        if self.speech.inflection_supported:
            orig = self.speech.get_inflection()
            self.assertEqual(orig, self.speech.inflection)
            self.assertIsInstance(self.speech.inflection_min, int)
            self.assertIsInstance(self.speech.inflection_max, int)
            self.speech.set_inflection(50)
            self.speech.inflection = orig
        else:
            with self.assertRaises(UnsupportedError):
                self.speech.set_inflection(50)
            with self.assertRaises(UnsupportedError):
                self.speech.get_inflection()

    def test_set_engine_valid(self):
        engines = self.speech.get_engines()
        if "SAPI5" in engines:
            self.speech.set_engine("SAPI5")
            self.assertEqual(self.speech.engine_used, "SAPI5")
            # Test case-insensitivity
            self.speech.set_engine("sapi5")
            self.assertEqual(self.speech.engine_used, "SAPI5")
            # Test ScreenReaderId enum
            self.speech.set_engine(ScreenReaderId.SAPI5)
            self.assertEqual(self.speech.engine_used, "SAPI5")
            # Test integer ID
            self.speech.set_engine(int(ScreenReaderId.SAPI5))
            self.assertEqual(self.speech.engine_used, "SAPI5")

    def test_set_engine_unsupported(self):
        with self.assertRaises(UnsupportedError):
            self.speech.set_engine("NonExistentEngineX")
        with self.assertRaises(EngineError):
            self.speech.set_engine("NonExistentEngineX")
        with self.assertRaises(EngineError):
            self.speech.set_engine(99999)

    def test_set_engine_invalid_type(self):
        with self.assertRaises(TypeError):
            self.speech.set_engine(["SAPI5"])  # type: ignore


if __name__ == "__main__":
    unittest.main()
