"""
Unit tests for screen reader queries and availability checks.
"""
import unittest
from UniversalSpeech import UniversalSpeech, ScreenReaderInfo, ScreenReaderId


class TestScreenReaders(unittest.TestCase):
    def setUp(self):
        self.speech = UniversalSpeech()

    def test_screen_reader_info_dataclass(self):
        info = ScreenReaderInfo(id=2, name="NVDA", available=True)
        self.assertEqual(info.id, 2)
        self.assertEqual(info.name, "NVDA")
        self.assertTrue(info.available)
        self.assertEqual(str(info), "NVDA")
        self.assertIn("ScreenReaderInfo(id=2, name='NVDA', available=True)", repr(info))

    def test_current_screen_reader_name(self):
        name = self.speech.current_screen_reader_name
        self.assertIsInstance(name, str)
        # On Windows, at least SAPI5 or a running screen reader should be returned
        self.assertTrue(len(name) > 0)

    def test_current_screen_reader_id(self):
        reader_id = self.speech.current_screen_reader_id
        self.assertIsInstance(reader_id, int)
        self.assertGreaterEqual(reader_id, 0)

    def test_get_supported_screen_readers(self):
        readers = self.speech.get_supported_screen_readers()
        self.assertIsInstance(readers, list)
        self.assertEqual(len(readers), 10)
        # Check standard known readers are in the list
        self.assertIn("NVDA", readers)
        self.assertIn("Jaws", readers)
        self.assertIn("SAPI5", readers)

    def test_get_screen_readers(self):
        readers_info = self.speech.get_screen_readers()
        self.assertIsInstance(readers_info, list)
        self.assertEqual(len(readers_info), 10)
        for r in readers_info:
            self.assertIsInstance(r, ScreenReaderInfo)
            self.assertIsInstance(r.id, int)
            self.assertIsInstance(r.name, str)
            self.assertIsInstance(r.available, bool)

    def test_individual_availability_checks(self):
        self.assertIsInstance(self.speech.nvda_is_available(), bool)
        self.assertIsInstance(self.speech.jaws_is_available(), bool)
        self.assertIsInstance(self.speech.sapi_is_available(), bool)
        self.assertIsInstance(self.speech.system_access_is_available(), bool)
        self.assertIsInstance(self.speech.supernova_is_available(), bool)
        self.assertIsInstance(self.speech.window_eyes_is_available(), bool)
        self.assertIsInstance(self.speech.cobra_is_available(), bool)
        self.assertIsInstance(self.speech.zoomtext_is_available(), bool)
        # On standard Windows, SAPI is always available
        self.assertTrue(self.speech.sapi_is_available())


if __name__ == "__main__":
    unittest.main()
