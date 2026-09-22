"""
DLL loader and ctypes setup for UniversalSpeech.
"""
import os
import sys
import ctypes
from typing import Optional
from .exceptions import DLLFileNotFoundError


class Loader:
    """
    Loader class for loading the UniversalSpeech.dll library.

    This class provides functionality to check for the existence of
    required DLL files and load the UniversalSpeech.dll library using ctypes.

    Attributes:
        __current_dir (str): The current directory where the package resides.
        __dll_files (list): A list of required DLL files.
        __lib_folder (str): The folder name based on the system architecture.
    """

    def __init__(self) -> None:
        self.__current_dir = os.path.dirname(os.path.abspath(__file__))
        self.__dll_files = [
            'dolapi.dll',
            'jfwapi.dll',
            'nvdaControllerClient.dll',
            'SAAPI32.dll',
            'UniversalSpeech.dll',
            'UniversalSpeech.tlb',
        ]
        # sys.maxsize > 2**32 reliably detects 64-bit Python across platforms
        self.__lib_folder = "lib64" if sys.maxsize > 2**32 else "lib"
        self.__dll_directory_handle = None

    def _files_check(self) -> bool:
        """
        Checks for the existence of required DLL files.

        Returns:
            bool: True if all required DLL files exist, False otherwise.
        """
        lib_folder = os.path.join(self.__current_dir, self.__lib_folder)
        if not os.path.isdir(lib_folder):
            return False

        current_dll_files = set(os.listdir(lib_folder))
        for file in self.__dll_files:
            if file not in current_dll_files:
                return False

        return True

    def load(self) -> ctypes.CDLL:
        """
        Loads the UniversalSpeech.dll library using ctypes and configures C signatures.

        Returns:
            ctypes.CDLL: The ctypes object representing the loaded library.

        Raises:
            DLLFileNotFoundError: Raised if any required DLL file is missing.
        """
        if not self._files_check():
            raise DLLFileNotFoundError("Missing dll files.")

        lib_folder = os.path.join(self.__current_dir, self.__lib_folder)

        # On Windows with Python 3.8+, add the directory containing dependencies to the DLL search path
        if hasattr(os, "add_dll_directory") and os.path.isdir(lib_folder):
            try:
                self.__dll_directory_handle = os.add_dll_directory(lib_folder)
            except OSError:
                pass

        # Specify the full path to the DLL
        dll_path = os.path.join(lib_folder, "UniversalSpeech.dll")
        uspeech = ctypes.CDLL(dll_path)

        # Configure ctypes signatures for core speech functions
        self._configure_signatures(uspeech)

        return uspeech

    @staticmethod
    def _configure_signatures(uspeech: ctypes.CDLL) -> None:
        """Configures restype and argtypes for exported DLL functions."""
        # Core speech functions
        if hasattr(uspeech, "speechGetString"):
            uspeech.speechGetString.restype = ctypes.c_wchar_p
            uspeech.speechGetString.argtypes = [ctypes.c_int]

        if hasattr(uspeech, "speechGetStringA"):
            uspeech.speechGetStringA.restype = ctypes.c_char_p
            uspeech.speechGetStringA.argtypes = [ctypes.c_int]

        if hasattr(uspeech, "speechSay"):
            uspeech.speechSay.restype = ctypes.c_int
            uspeech.speechSay.argtypes = [ctypes.c_wchar_p, ctypes.c_int]

        if hasattr(uspeech, "speechSayA"):
            uspeech.speechSayA.restype = ctypes.c_int
            uspeech.speechSayA.argtypes = [ctypes.c_char_p, ctypes.c_int]

        if hasattr(uspeech, "brailleDisplay"):
            uspeech.brailleDisplay.restype = ctypes.c_int
            uspeech.brailleDisplay.argtypes = [ctypes.c_wchar_p]

        if hasattr(uspeech, "brailleDisplayA"):
            uspeech.brailleDisplayA.restype = ctypes.c_int
            uspeech.brailleDisplayA.argtypes = [ctypes.c_char_p]

        if hasattr(uspeech, "speechStop"):
            uspeech.speechStop.restype = ctypes.c_int
            uspeech.speechStop.argtypes = []

        if hasattr(uspeech, "speechGetValue"):
            uspeech.speechGetValue.restype = ctypes.c_int
            uspeech.speechGetValue.argtypes = [ctypes.c_int]

        if hasattr(uspeech, "speechSetValue"):
            uspeech.speechSetValue.restype = ctypes.c_int
            uspeech.speechSetValue.argtypes = [ctypes.c_int, ctypes.c_int]

        if hasattr(uspeech, "speechSetString"):
            uspeech.speechSetString.restype = ctypes.c_int
            uspeech.speechSetString.argtypes = [ctypes.c_int, ctypes.c_wchar_p]

        # Screen reader inquiry functions
        if hasattr(uspeech, "getCurrentScreenReader"):
            uspeech.getCurrentScreenReader.restype = ctypes.c_int
            uspeech.getCurrentScreenReader.argtypes = []

        if hasattr(uspeech, "getCurrentScreenReaderNameW"):
            uspeech.getCurrentScreenReaderNameW.restype = ctypes.c_wchar_p
            uspeech.getCurrentScreenReaderNameW.argtypes = []

        if hasattr(uspeech, "getSupportedScreenReadersCount"):
            uspeech.getSupportedScreenReadersCount.restype = ctypes.c_int
            uspeech.getSupportedScreenReadersCount.argtypes = []

        if hasattr(uspeech, "getScreenReaderNameW"):
            uspeech.getScreenReaderNameW.restype = ctypes.c_wchar_p
            uspeech.getScreenReaderNameW.argtypes = [ctypes.c_int]

        # Individual screen reader availability
        for func_name in [
            "nvdaIsAvailable",
            "jfwIsAvailable",
            "sapiIsAvailable",
            "saIsAvailable",
            "dolIsAvailable",
            "weIsAvailable",
            "cbrIsAvailable",
            "ztIsAvailable",
            "narIsAvailable",
        ]:
            if hasattr(uspeech, func_name):
                func = getattr(uspeech, func_name)
                func.restype = ctypes.c_int
                func.argtypes = []

        # SAPI-specific playback functions
        if hasattr(uspeech, "sapiWait"):
            uspeech.sapiWait.restype = ctypes.c_int
            uspeech.sapiWait.argtypes = []

        if hasattr(uspeech, "sapiIsSpeaking"):
            uspeech.sapiIsSpeaking.restype = ctypes.c_int
            uspeech.sapiIsSpeaking.argtypes = []

        if hasattr(uspeech, "sapiIsPaused"):
            uspeech.sapiIsPaused.restype = ctypes.c_int
            uspeech.sapiIsPaused.argtypes = []

        if hasattr(uspeech, "sapiSetPaused"):
            uspeech.sapiSetPaused.restype = ctypes.c_int
            uspeech.sapiSetPaused.argtypes = [ctypes.c_int]

        if hasattr(uspeech, "sapiSaySSMLW"):
            uspeech.sapiSaySSMLW.restype = ctypes.c_int
            uspeech.sapiSaySSMLW.argtypes = [ctypes.c_wchar_p]


__all__ = ["Loader"]
