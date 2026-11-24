"""
Regression tests for issues found while reviewing the v3-fixes branch:
SSIP deadlock and handshake, Linux wait/busy reporting, input validation,
SSML fallback and CLI stdin handling.
"""
import io
import socket
import sys
import threading
import unittest
from unittest.mock import MagicMock, patch

from UniversalSpeech import UniversalSpeech
from UniversalSpeech.__main__ import main
from UniversalSpeech.backends.base import BaseBackend
from UniversalSpeech.backends.linux import LinuxBackend, _SSIPSocketClient


def _bare_ssip_client(sock):
    client = _SSIPSocketClient.__new__(_SSIPSocketClient)
    client.sock = sock
    client._connected = True
    client._recv_buffer = ""
    client._lock = threading.Lock()
    client._current_rate = None
    client._current_volume = None
    client._current_pitch = None
    return client


class _FakeBackend(BaseBackend):
    def __init__(self):
        self.spoken = []

    def say(self, msg, interrupt=True):
        self.spoken.append(msg)
        return 1

    def stop(self):
        return 1

    @property
    def engine_used(self):
        return "Fake"

    def get_diagnostics(self):
        return {}


class TestSSIPClient(unittest.TestCase):
    def _run_with_deadline(self, func, seconds=3.0):
        result = {}
        th = threading.Thread(target=lambda: result.setdefault("value", func()), daemon=True)
        th.start()
        th.join(seconds)
        self.assertFalse(th.is_alive(), "SSIP call deadlocked instead of returning")
        return result.get("value")

    def test_command_timeout_does_not_deadlock(self):
        a, b = socket.socketpair()
        try:
            a.settimeout(0.2)  # peer never answers
            client = _bare_ssip_client(a)
            self.assertIsNone(self._run_with_deadline(lambda: client._send_command("CANCEL self")))
            self.assertFalse(client.is_connected)
        finally:
            b.close()

    def test_speak_timeout_does_not_deadlock(self):
        a, b = socket.socketpair()
        try:
            a.settimeout(0.2)
            client = _bare_ssip_client(a)
            self.assertFalse(self._run_with_deadline(lambda: client.speak("hello")))
            self.assertFalse(client.is_connected)
        finally:
            b.close()

    def test_connection_closed_by_server_does_not_deadlock(self):
        a, b = socket.socketpair()
        a.settimeout(1.0)
        b.close()
        client = _bare_ssip_client(a)
        self.assertIsNone(self._run_with_deadline(lambda: client._send_command("CANCEL self")))
        self.assertFalse(client.is_connected)

    def test_connect_does_not_wait_for_greeting(self):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [b"208 OK CLIENT NAME SET\r\n"]
        with patch("socket.socket", return_value=mock_sock):
            client = _SSIPSocketClient(port=6560)
        self.assertTrue(client.is_connected)
        first_sent = mock_sock.sendall.call_args_list[0][0][0]
        self.assertTrue(first_sent.startswith(b"SET self CLIENT_NAME"))

    def test_rejected_client_name_is_not_connected(self):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [b"400 ERR\r\n"]
        with patch("socket.socket", return_value=mock_sock):
            client = _SSIPSocketClient(port=6560)
        self.assertFalse(client.is_connected)

    def test_failed_parameter_is_not_cached(self):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [b"410 ERR\r\n", b"203 OK RATE SET\r\n"]
        client = _bare_ssip_client(mock_sock)
        client.set_rate(10)
        self.assertIsNone(client._current_rate)
        client.set_rate(10)  # retried because the first attempt failed
        self.assertEqual(client._current_rate, 10)


class TestLinuxWaitAndBusy(unittest.TestCase):
    def _backend(self):
        backend = LinuxBackend.__new__(LinuxBackend)
        backend._active_engine_name = "auto"
        backend._current_engine = "test"
        backend._rate, backend._volume, backend._pitch = 50, 100, 50
        backend._process_lock = threading.Lock()
        backend._last_output = None
        backend._last_process = None
        backend._ssip_client = None
        backend._espeak_lib = None
        return backend

    def test_ssip_output_reports_wait_unsupported(self):
        backend = self._backend()
        backend._espeak_lib = MagicMock()  # library present but not used for output
        backend._last_output = "ssip"
        self.assertFalse(backend.wait_supported)
        self.assertFalse(backend.busy_supported)
        self.assertFalse(backend.wait())

    def test_espeak_cli_wait_uses_process(self):
        backend = self._backend()
        proc = MagicMock()
        proc.poll.return_value = None
        backend._last_process = proc
        backend._last_output = "espeak-cli"
        self.assertTrue(backend.wait_supported)
        self.assertTrue(backend.is_busy)
        self.assertTrue(backend.wait(timeout_ms=500))
        proc.wait.assert_called_once_with(timeout=0.5)

    def test_espeak_lib_wait_times_out(self):
        backend = self._backend()
        backend._espeak_lib = MagicMock()
        backend._espeak_lib.espeak_IsPlaying.return_value = 1
        backend._last_output = "espeak-lib"
        self.assertFalse(backend.wait(timeout_ms=50))
        backend._espeak_lib.espeak_IsPlaying.return_value = 0
        self.assertTrue(backend.wait(timeout_ms=50))


class TestInputValidationAndSSML(unittest.TestCase):
    def test_non_string_messages_rejected(self):
        speech = UniversalSpeech(backend=_FakeBackend())
        for bad in (None, 123):
            with self.assertRaises(TypeError):
                speech.say(bad)  # type: ignore[arg-type]
            with self.assertRaises(TypeError):
                speech.braille(bad)  # type: ignore[arg-type]
            with self.assertRaises(TypeError):
                speech.say_ssml(bad)  # type: ignore[arg-type]

    def test_ssml_fallback_strips_tags_and_entities(self):
        backend = _FakeBackend()
        UniversalSpeech(backend=backend).say_ssml(
            '<speak>Hello <break time="1s"/>Tom &amp; Jerry</speak>'
        )
        self.assertEqual(backend.spoken[-1], "Hello Tom & Jerry")


class TestCliStdin(unittest.TestCase):
    def _run_cli(self, args, stdin):
        backend = _FakeBackend()
        orig = sys.stdin
        try:
            sys.stdin = stdin
            with patch("UniversalSpeech.__main__.UniversalSpeech",
                       side_effect=lambda **kw: UniversalSpeech(backend=backend, **kw)):
                ret = main(args)
        finally:
            sys.stdin = orig
        return ret, backend

    def test_dash_reads_stdin(self):
        stdin = io.StringIO("from stdin")
        stdin.isatty = lambda: False  # type: ignore[method-assign]
        ret, backend = self._run_cli(["-"], stdin)
        self.assertEqual(ret, 0)
        self.assertEqual(backend.spoken, ["from stdin"])

    def test_slow_pipe_is_not_ignored(self):
        """Data written after a delay must still be read (previously a 0-timeout poll dropped it)."""
        r, w = socket.socketpair()
        stream = r.makefile("r", encoding="utf-8")

        def writer():
            import time
            time.sleep(0.3)
            w.sendall(b"late message")
            w.close()

        threading.Thread(target=writer, daemon=True).start()
        stream.isatty = lambda: False  # type: ignore[method-assign]
        try:
            ret, backend = self._run_cli(["-"], stream)
        finally:
            stream.close()
            r.close()
        self.assertEqual(ret, 0)
        self.assertEqual(backend.spoken, ["late message"])

    def test_interactive_terminal_is_not_read(self):
        stdin = MagicMock()
        stdin.isatty.return_value = True
        ret, backend = self._run_cli([], stdin)
        self.assertEqual(ret, 0)
        stdin.read.assert_not_called()
        self.assertEqual(backend.spoken, [])


if __name__ == "__main__":
    unittest.main()
