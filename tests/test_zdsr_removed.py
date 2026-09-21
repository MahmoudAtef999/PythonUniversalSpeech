import os
import unittest
import UniversalSpeech


class TestZDSRRemoved(unittest.TestCase):
    """Test that ZDSRAPI.dll is removed and the library functions cleanly without it."""

    def test_zdsrapi_dll_not_present(self):
        base_dir = os.path.dirname(UniversalSpeech.__file__)
        lib32_zdsr = os.path.join(base_dir, "lib", "ZDSRAPI.dll")
        lib64_zdsr = os.path.join(base_dir, "lib64", "ZDSRAPI.dll")

        self.assertFalse(
            os.path.exists(lib32_zdsr),
            f"ZDSRAPI.dll should not exist in {lib32_zdsr}",
        )
        self.assertFalse(
            os.path.exists(lib64_zdsr),
            f"ZDSRAPI.dll should not exist in {lib64_zdsr}",
        )

    def test_library_functions_without_zdsrapi(self):
        speech = UniversalSpeech.UniversalSpeech()
        engines = speech.get_engines()
        self.assertIsInstance(engines, dict)
        if "ZDSR" in engines:
            self.assertFalse(
                engines["ZDSR"]["available"],
                "ZDSR engine should not be available without ZDSRAPI.dll",
            )
        # Verify speech functions work cleanly
        speech.enable_native_speech(True)
        speech.say("Testing without ZDSRAPI", interrupt=True)
        speech.stop()


if __name__ == "__main__":
    unittest.main()
