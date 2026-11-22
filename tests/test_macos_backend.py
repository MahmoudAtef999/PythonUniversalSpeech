"""
Unit tests for MacOSBackend (VoiceOver AppleScript and native macOS say synthesis).
"""
import unittest
from unittest.mock import MagicMock, patch
from UniversalSpeech.backends.macos import MacOSBackend
from UniversalSpeech import UniversalSpeech, Voice
from UniversalSpeech.exceptions import EngineError, VoiceError


SAMPLE_SAY_VOICES_OUTPUT = b"""Alex                en_US    # Most people recognize me by my voice.
Samantha            en_US    # Hello, my name is Samantha.
Tarik               ar_SA    # \xd9\x85\xd8\xb1\xd8\xad\xd8\xa8\xd8\xa7\xd8\x8c \xd8\xa7\xd8\xb3\xd9\x85\xd9\x8a \xd8\xb7\xd8\xa7\xd8\xb1\xd9\x82.
"""


class TestMacOSBackend(unittest.TestCase):
    """Test MacOSBackend under simulated macOS environments without requiring actual Mac hardware."""

    def test_voiceover_detection_and_speech(self):
        """Simulate VoiceOver running and verify AppleScript execution."""
        with patch("shutil.which", return_value="/usr/bin/osascript"), \
             patch("subprocess.run") as mock_run, \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=True):

            mock_run.return_value = MagicMock(returncode=0)
            backend = MacOSBackend()
            self.assertTrue(backend.voiceover_is_available())
            self.assertEqual(backend.current_screen_reader_name, "VoiceOver")
            self.assertEqual(backend.current_screen_reader_id, 200)

            # Test speaking with VoiceOver
            res = backend.say("Testing VoiceOver on macOS")
            self.assertEqual(res, 1)

            # Test stop
            self.assertEqual(backend.stop(), 1)

    def test_voiceover_failure_falls_back_to_say(self):
        """When VoiceOver AppleScript returns non-zero code, fall back to /say binary."""
        with patch("shutil.which", side_effect=lambda x: f"/usr/bin/{x}"), \
             patch("subprocess.run") as mock_run, \
             patch("subprocess.Popen") as mock_popen, \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=True):

            # Simulate osascript failing (e.g. AppleScript permission denied)
            mock_run.return_value = MagicMock(returncode=1)
            mock_process = MagicMock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            backend = MacOSBackend()
            res = backend.say("Testing fallback when VoiceOver AppleScript fails")
            self.assertEqual(res, 1)
            # Verify say was invoked via Popen fallback
            mock_popen.assert_called_once()

    def test_say_voices_parsing_and_selection(self):
        """Test parsing `say -v '?'` output into Voice objects and setting active voice."""
        with patch("shutil.which", return_value="/usr/bin/say"), \
             patch("subprocess.check_output", return_value=SAMPLE_SAY_VOICES_OUTPUT), \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=False):

            backend = MacOSBackend()
            voices = backend.get_voices()
            self.assertEqual(len(voices), 3)
            self.assertEqual(voices[0].name, "Alex")
            self.assertEqual(voices[0].language, "en_US")
            self.assertEqual(voices[1].name, "Samantha")
            self.assertEqual(voices[2].name, "Tarik")
            self.assertEqual(voices[2].language, "ar_SA")

            # Voice selection by name
            backend.set_voice("Samantha")
            self.assertEqual(backend.get_voice().name, "Samantha")

            # Voice selection by ID
            backend.set_voice(0)
            self.assertEqual(backend.get_voice().name, "Alex")

            # Voice selection by object
            backend.set_voice(voices[2])
            self.assertEqual(backend.get_voice().name, "Tarik")

            # Invalid voice name raises VoiceError
            with self.assertRaises(VoiceError):
                backend.set_voice("NonExistentVoice")

    def test_macos_parameters_and_ranges(self):
        """Test rate and volume on MacOSBackend."""
        with patch("shutil.which", return_value="/usr/bin/say"), \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=False):

            backend = MacOSBackend()
            self.assertTrue(backend.rate_supported)
            self.assertEqual(backend.rate_range, (0, 100))
            backend.rate = 75
            self.assertEqual(backend.rate, 75)

            self.assertTrue(backend.volume_supported)
            self.assertEqual(backend.volume_range, (0, 100))
            backend.volume = 85
            self.assertEqual(backend.volume, 85)

    def test_macos_engines_and_diagnostics(self):
        """Test get_engines and get_diagnostics on MacOSBackend."""
        with patch("shutil.which", return_value="/usr/bin/say"), \
             patch("subprocess.check_output", return_value=SAMPLE_SAY_VOICES_OUTPUT), \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=False):

            backend = MacOSBackend()
            engines = backend.get_engines()
            self.assertIn("voiceover", engines)
            self.assertIn("say", engines)
            self.assertTrue(engines["say"]["available"])

            diag = backend.get_diagnostics()
            self.assertEqual(diag["platform"], "darwin")
            self.assertEqual(diag["backend"], "MacOSBackend")
            self.assertEqual(diag["voices_count"], 3)
            self.assertEqual(diag["active_voice"]["name"], "Alex")

            summary = backend.diagnostics_summary()
            self.assertIn("MacOSBackend", summary)

    def test_universal_speech_with_macos_backend(self):
        """Verify UniversalSpeech facade properly delegates to MacOSBackend."""
        with patch("shutil.which", return_value="/usr/bin/say"), \
             patch.object(MacOSBackend, "voiceover_is_available", return_value=False):

            macos_backend = MacOSBackend()
            speech = UniversalSpeech(backend=macos_backend)

            self.assertEqual(speech.backend, macos_backend)
            speech.rate = 70
            self.assertEqual(speech.rate, 70)
            self.assertEqual(macos_backend.rate, 70)

            diag = speech.get_diagnostics()
            self.assertEqual(diag["platform"], "darwin")


if __name__ == "__main__":
    unittest.main()
