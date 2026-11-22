"""
Unit tests for LinuxBackend (Speech Dispatcher SSIP/CLI, eSpeak, and Orca screen reader).
"""
import unittest
from unittest.mock import MagicMock, patch
import socket
from UniversalSpeech.backends.linux import LinuxBackend, _SSIPSocketClient
from UniversalSpeech import UniversalSpeech
from UniversalSpeech.exceptions import EngineError


class TestLinuxBackend(unittest.TestCase):
    """Test LinuxBackend in mocked environments without requiring a physical Linux display."""

    def test_ssip_socket_client_workflow(self):
        """Verify _SSIPSocketClient speaks and controls parameters over a simulated socket."""
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [
            b"200 OK SPEECH DISPATCHER READY\r\n",
            b"200 OK CLIENT NAME SET\r\n",
            b"230 OK RECEIVING DATA\r\n",
            b"225-1\r\n225 OK MESSAGE QUEUED\r\n",
            b"200 OK CANCELLED\r\n",
            b"200 OK RATE SET\r\n",
            b"200 OK VOLUME SET\r\n",
            b"200 OK PITCH SET\r\n",
            # Second speak call with dot-starting message
            b"230 OK RECEIVING DATA\r\n",
            b"225-2\r\n225 OK MESSAGE QUEUED\r\n",
        ]

        with patch("socket.socket", return_value=mock_sock):
            client = _SSIPSocketClient(port=6560)
            self.assertTrue(client.is_connected)

            # Test speak with standard text
            res = client.speak("Hello from Linux SSIP")
            self.assertTrue(res)

            # Test cancel
            self.assertTrue(client.cancel())

            # Test parameters (sent when changed)
            client.set_rate(20)
            client.set_volume(80)
            client.set_pitch(10)

            # Redundant parameter calls should not send across socket
            client.set_rate(20)
            client.set_volume(80)
            client.set_pitch(10)

            # Test speak with dot-starting message (. and ...test)
            res2 = client.speak("...leading dot message\n.second line dot")
            self.assertTrue(res2)

            # Close
            client.close()
            self.assertFalse(client.is_connected)

    def test_linux_backend_properties_and_ranges(self):
        """Test parameter getters, setters, and ranges on LinuxBackend."""
        with patch.object(LinuxBackend, "_init_speechd"), \
             patch.object(LinuxBackend, "_init_espeak"):
            backend = LinuxBackend()

            # Rate
            self.assertTrue(backend.rate_supported)
            self.assertEqual(backend.rate_range, (0, 100))
            backend.rate = 80
            self.assertEqual(backend.rate, 80)
            self.assertEqual(backend.get_rate(), 80)

            # Volume
            self.assertTrue(backend.volume_supported)
            self.assertEqual(backend.volume_range, (0, 100))
            backend.volume = 90
            self.assertEqual(backend.volume, 90)

            # Pitch
            self.assertTrue(backend.pitch_supported)
            self.assertEqual(backend.pitch_range, (0, 100))
            backend.pitch = 40
            self.assertEqual(backend.pitch, 40)

    def test_linux_backend_orca_detection(self):
        """Test Orca screen reader detection and version query."""
        with patch.object(LinuxBackend, "_init_speechd"), \
             patch.object(LinuxBackend, "_init_espeak"), \
             patch("shutil.which", return_value="/usr/bin/orca"), \
             patch("subprocess.run") as mock_run, \
             patch("subprocess.check_output", return_value=b"Orca 45.1\n"):

            mock_run.return_value = MagicMock(returncode=0)

            backend = LinuxBackend()
            self.assertTrue(backend.orca_is_available())
            self.assertEqual(backend.current_screen_reader_name, "Orca")
            self.assertEqual(backend.current_screen_reader_id, 100)
            self.assertEqual(backend.orca_get_version(), "45.1")

            readers = backend.get_screen_readers()
            self.assertEqual(len(readers), 1)
            self.assertEqual(readers[0].name, "Orca")
            self.assertTrue(readers[0].available)

            diag = backend.get_diagnostics()
            self.assertEqual(diag["screen_readers"][0]["version"], "45.1")

    def test_linux_backend_engines_and_diagnostics(self):
        """Test get_engines, set_engine, and get_diagnostics."""
        with patch.object(LinuxBackend, "_init_speechd"), \
             patch.object(LinuxBackend, "_init_espeak"), \
             patch("shutil.which", side_effect=lambda x: f"/usr/bin/{x}"):

            backend = LinuxBackend()
            engines = backend.get_engines()
            self.assertIn("speech-dispatcher", engines)
            self.assertIn("espeak", engines)
            self.assertTrue(engines["speech-dispatcher"]["available"])
            self.assertTrue(engines["espeak"]["available"])

            # Switch to espeak
            backend.set_engine("espeak")
            self.assertEqual(backend.engine_used, "eSpeak")

            # Diagnostics
            diag = backend.get_diagnostics()
            self.assertEqual(diag["platform"], "linux")
            self.assertEqual(diag["backend"], "LinuxBackend")
            self.assertIn("capabilities", diag)
            self.assertIn("parameters", diag)

            summary = backend.diagnostics_summary()
            self.assertIn("LinuxBackend", summary)

    def test_universal_speech_with_linux_backend(self):
        """Verify UniversalSpeech facade properly delegates to LinuxBackend."""
        with patch.object(LinuxBackend, "_init_speechd"), \
             patch.object(LinuxBackend, "_init_espeak"):
            linux_backend = LinuxBackend()
            speech = UniversalSpeech(backend=linux_backend)

            self.assertEqual(speech.backend, linux_backend)
            speech.rate = 65
            self.assertEqual(speech.rate, 65)
            self.assertEqual(linux_backend.rate, 65)

            # Check diagnostics delegation
            diag = speech.get_diagnostics()
            self.assertEqual(diag["platform"], "linux")


if __name__ == "__main__":
    unittest.main()
