import unittest
import sys
import ctypes
from unittest.mock import patch
from UniversalSpeech.load import Loader
from UniversalSpeech.exceptions import DLLFileNotFoundError, PlatformError


@unittest.skipUnless(sys.platform == "win32", "Windows DLL Loader tests require Windows")
class TestLoader(unittest.TestCase):
    """Test DLL Loader behavior and error handling."""

    def test_loader_init(self):
        loader = Loader()
        self.assertIsNotNone(loader)

    def test_files_check_success(self):
        loader = Loader()
        self.assertTrue(loader._files_check())

    def test_load_success(self):
        loader = Loader()
        uspeech = loader.load()
        self.assertIsInstance(uspeech, ctypes.CDLL)

    def test_load_cached_instance(self):
        loader1 = Loader()
        loader2 = Loader()
        uspeech1 = loader1.load()
        uspeech2 = loader2.load()
        self.assertIs(uspeech1, uspeech2)

    def test_missing_dll_raises_error(self):
        loader = Loader()
        # Simulate a missing required DLL by adding a non-existent file to the required list
        loader._Loader__dll_files.append("non_existent_dummy_file.dll")
        self.assertFalse(loader._files_check())
        with self.assertRaises(DLLFileNotFoundError):
            loader.load()

    def test_missing_lib_folder(self):
        loader = Loader()
        # Simulate non-existent folder
        loader._Loader__lib_folder = "non_existent_folder_xyz"
        self.assertFalse(loader._files_check())
        with self.assertRaises(DLLFileNotFoundError):
            loader.load()

    def test_unsupported_platform_raises_error(self):
        loader = Loader()
        with patch.object(sys, "platform", "linux"):
            with self.assertRaises(PlatformError):
                loader.load()


if __name__ == "__main__":
    unittest.main()
