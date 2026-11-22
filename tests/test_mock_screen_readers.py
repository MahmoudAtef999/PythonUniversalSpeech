"""
Mock-based unit tests for screen reader queries, version lookups,
scripting functions, and speech parameters under simulated environments.
"""
import unittest
import sys
from unittest.mock import MagicMock, patch
import ctypes
from UniversalSpeech import UniversalSpeech, ScreenReaderInfo, ScreenReaderId
from UniversalSpeech.constants import (
    PITCH, PITCH_MIN, PITCH_MAX, PITCH_SUPPORTED,
    INFLECTION, INFLECTION_MIN, INFLECTION_MAX, INFLECTION_SUPPORTED,
)


@unittest.skipUnless(sys.platform == "win32", "Windows screen reader tests require Windows")
class TestMockScreenReaders(unittest.TestCase):
    """Test screen reader branches and features when simulated as running."""

    def setUp(self):
        self.speech = UniversalSpeech()
        # Access the underlying mockable ctypes object via backend
        self.uspeech = self.speech.backend.uspeech

    def test_mock_nvda_active_and_version(self):
        """Simulate NVDA running with a specific version string."""
        def fake_nvda_version(buf, size):
            ver_bytes = b"2026.3.1\x00"
            ctypes.memmove(buf, ver_bytes, len(ver_bytes))
            return 1

        with patch.object(self.uspeech, "nvdaIsAvailable", return_value=1), \
             patch.object(self.uspeech, "nvdaGetRunningVersion", side_effect=fake_nvda_version):
            self.assertTrue(self.speech.nvda_is_available())
            self.assertEqual(self.speech.nvda_get_version(), "2026.3.1")
            # Verify _is_reader_available helper
            self.assertTrue(self.speech._is_reader_available(2, "NVDA"))

    def test_mock_jaws_active_scripting_and_settings(self):
        """Simulate JAWS running with version, settings path, and scripting."""
        def fake_jaws_version(buf, size):
            ver_bytes = b"2025.2.1\x00"
            ctypes.memmove(buf, ver_bytes, len(ver_bytes))
            return 1

        def fake_jaws_settings_dir(buf, size):
            path_bytes = b"C:\\Users\\User\\AppData\\Roaming\\Freedom Scientific\\Jaws\\2025\\Settings\x00"
            ctypes.memmove(buf, path_bytes, len(path_bytes))
            return 1

        with patch.object(self.uspeech, "jfwIsAvailable", return_value=1), \
             patch.object(self.uspeech, "jfwGetRunningVersion", side_effect=fake_jaws_version), \
             patch.object(self.uspeech, "jfwGetUserSettingsDirectory", side_effect=fake_jaws_settings_dir), \
             patch.object(self.uspeech, "jfwRunScriptW", return_value=1), \
             patch.object(self.uspeech, "jfwRunFunctionW", return_value=1):

            self.assertTrue(self.speech.jaws_is_available())
            self.assertEqual(self.speech.jfw_get_version(), "2025.2.1")
            self.assertEqual(self.speech.jaws_get_version(), "2025.2.1")
            self.assertEqual(
                self.speech.jaws_get_user_settings_directory(),
                "C:\\Users\\User\\AppData\\Roaming\\Freedom Scientific\\Jaws\\2025\\Settings",
            )
            self.assertTrue(self.speech.jaws_run_script("SayLine"))
            self.assertTrue(self.speech.jaws_run_function('SayString("Hello")'))
            self.assertTrue(self.speech._is_reader_available(0, "Jaws"))

    def test_mock_all_screen_readers_available(self):
        """Test individual reader availability flags when mocked as active."""
        readers_to_mock = [
            ("dolIsAvailable", "supernova_is_available", "Supernova"),
            ("weIsAvailable", "window_eyes_is_available", "Windows eye"),
            ("saIsAvailable", "system_access_is_available", "System access"),
            ("cbrIsAvailable", "cobra_is_available", "Cobra"),
            ("ztIsAvailable", "zoomtext_is_available", "ZoomText"),
            ("narIsAvailable", "narrator_is_available", "Narrator"),
            ("zdsrIsAvailable", "zdsr_is_available", "ZDSR"),
        ]
        for func_name, method_name, reader_label in readers_to_mock:
            with patch.object(self.uspeech, func_name, return_value=1):
                checker_method = getattr(self.speech, method_name)
                self.assertTrue(checker_method(), f"{method_name} should return True when {func_name} returns 1")
                self.assertTrue(
                    self.speech._is_reader_available(99, reader_label),
                    f"_is_reader_available should be True for {reader_label}",
                )

    def test_mock_pitch_and_inflection_support(self):
        """Simulate an engine that fully supports pitch and inflection control."""
        values = {
            PITCH_SUPPORTED: 1,
            PITCH: 50,
            PITCH_MIN: 0,
            PITCH_MAX: 100,
            INFLECTION_SUPPORTED: 1,
            INFLECTION: 30,
            INFLECTION_MIN: 0,
            INFLECTION_MAX: 100,
        }

        def fake_get_value(param):
            return values.get(param, 0)

        def fake_set_value(param, val):
            values[param] = val
            return 1

        with patch.object(self.speech.backend, "get_value", side_effect=fake_get_value), \
             patch.object(self.speech.backend, "set_value", side_effect=fake_set_value):

            # Pitch verification
            self.assertTrue(self.speech.pitch_supported)
            self.assertEqual(self.speech.get_pitch(), 50)
            self.assertEqual(self.speech.pitch, 50)
            self.assertEqual(self.speech.pitch_range, (0, 100))
            self.speech.pitch = 75
            self.assertEqual(self.speech.pitch, 75)

            # Inflection verification
            self.assertTrue(self.speech.inflection_supported)
            self.assertEqual(self.speech.get_inflection(), 30)
            self.assertEqual(self.speech.inflection, 30)
            self.assertEqual(self.speech.inflection_range, (0, 100))
            self.speech.inflection = 60
            self.assertEqual(self.speech.inflection, 60)


if __name__ == "__main__":
    unittest.main()
