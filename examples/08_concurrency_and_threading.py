"""
Example 08: Thread-Safe Concurrency & Worker Notifications
----------------------------------------------------------
Demonstrates using UniversalSpeech safely across multiple background threads
(e.g., worker tasks, progress updates, asynchronous event alerts).
"""
import sys
import os
import time
import threading

# Ensure repository root is in sys.path when running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from UniversalSpeech import UniversalSpeech


def background_worker(worker_id: int, speech: UniversalSpeech):
    print(f"[Worker {worker_id}] Task started.")
    time.sleep(0.5 * worker_id)

    # Safely speak from background worker thread
    msg = f"Worker {worker_id} finished processing."
    print(f"[Worker {worker_id}] Announcing completion: '{msg}'")
    speech.say(msg, interrupt=False)


def main():
    print("=== Multi-Threaded Speech Notifications Demo ===")

    # Create a shared UniversalSpeech instance (or each worker can instantiate its own)
    with UniversalSpeech() as speech:
        threads = []
        for i in range(1, 4):
            t = threading.Thread(target=background_worker, args=(i, speech), name=f"WorkerThread-{i}")
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Allow final speech to complete
        if speech.wait_supported:
            speech.wait(timeout_ms=3000)

    print("All background threads completed successfully!")


if __name__ == "__main__":
    main()
