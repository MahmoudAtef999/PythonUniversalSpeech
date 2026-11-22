"""
Unit tests for thread safety and concurrent operations in UniversalSpeech.
"""
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
from UniversalSpeech import UniversalSpeech


class TestConcurrency(unittest.TestCase):
    """Test concurrent interactions across multiple worker threads."""

    def test_concurrent_speech_queries(self):
        """Ensure multiple threads can query speech parameters and engines concurrently without error."""
        errors = []

        def worker(thread_idx: int):
            try:
                speech = UniversalSpeech()
                # Query engines
                engines = speech.get_engines()
                if not engines:
                    raise RuntimeError("No engines returned")
                # Query diagnostics
                diag = speech.get_diagnostics()
                if "platform" not in diag:
                    raise RuntimeError("Invalid diagnostics")
                # Query properties
                _ = speech.engine_used
                _ = speech.current_screen_reader_name
                _ = speech.volume_supported
                _ = speech.rate_supported
            except Exception as e:
                errors.append((thread_idx, e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread errors encountered: {errors}")

    def test_thread_pool_executor(self):
        """Test concurrent operations using ThreadPoolExecutor."""
        speech = UniversalSpeech()

        def query_task(num: int):
            return (
                speech.engine_used,
                speech.current_screen_reader_id,
                speech.volume_supported,
                speech.is_busy,
            )

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(query_task, i) for i in range(16)]
            results = [f.result() for f in futures]

        self.assertEqual(len(results), 16)
        for r in results:
            self.assertIsInstance(r[0], str)
            self.assertIsInstance(r[1], int)
            self.assertIsInstance(r[2], bool)
            self.assertIsInstance(r[3], bool)


if __name__ == "__main__":
    unittest.main()
