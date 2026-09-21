import unittest
import UniversalSpeech
from UniversalSpeech.exceptions import DLLFileNotFoundError, UnsupportedError


class TestConstants(unittest.TestCase):
    """Test exported constants and exception types."""

    def test_parameter_identifiers(self):
        # range(0, 22)
        expected_range_constants = [
            (UniversalSpeech.VOLUME, 0),
            (UniversalSpeech.VOLUME_MAX, 1),
            (UniversalSpeech.VOLUME_MIN, 2),
            (UniversalSpeech.VOLUME_SUPPORTED, 3),
            (UniversalSpeech.RATE, 4),
            (UniversalSpeech.RATE_MAX, 5),
            (UniversalSpeech.RATE_MIN, 6),
            (UniversalSpeech.RATE_SUPPORTED, 7),
            (UniversalSpeech.PITCH, 8),
            (UniversalSpeech.PITCH_MAX, 9),
            (UniversalSpeech.PITCH_MIN, 10),
            (UniversalSpeech.PITCH_SUPPORTED, 11),
            (UniversalSpeech.INFLECTION, 12),
            (UniversalSpeech.INFLECTION_MAX, 13),
            (UniversalSpeech.INFLECTION_MIN, 14),
            (UniversalSpeech.INFLECTION_SUPPORTED, 15),
            (UniversalSpeech.PAUSED, 16),
            (UniversalSpeech.PAUSE_SUPPORTED, 17),
            (UniversalSpeech.BUSY, 18),
            (UniversalSpeech.BUSY_SUPPORTED, 19),
            (UniversalSpeech.WAIT, 20),
            (UniversalSpeech.WAIT_SUPPORTED, 21),
        ]
        for const_val, expected in expected_range_constants:
            self.assertEqual(const_val, expected)

    def test_hex_identifiers(self):
        self.assertEqual(UniversalSpeech.ENABLE_NATIVE_SPEECH, 0xFFFF)
        self.assertEqual(UniversalSpeech.VOICE, 0x10000)
        self.assertEqual(UniversalSpeech.LANGUAGE, 0x20000)
        self.assertEqual(UniversalSpeech.SUBENGINE, 0x30000)
        self.assertEqual(UniversalSpeech.ENGINE, 0x40000)
        self.assertEqual(UniversalSpeech.ENGINE_AVAILABLE, 0x50000)
        self.assertEqual(UniversalSpeech.AUTO_ENGINE, 0xFFFE)
        self.assertEqual(UniversalSpeech.USER_PARAM, 0x1000000)

    def test_exceptions_inheritance(self):
        self.assertTrue(issubclass(DLLFileNotFoundError, Exception))
        self.assertTrue(issubclass(UnsupportedError, Exception))


if __name__ == "__main__":
    unittest.main()
