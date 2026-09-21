import os
import sys
import ctypes
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
        Loads the UniversalSpeech.dll library using ctypes.

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

        return uspeech