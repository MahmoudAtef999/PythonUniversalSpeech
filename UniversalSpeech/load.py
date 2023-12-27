import os
import platform
import ctypes
from .exceptions import DLLFileNotFoundError

class Loader:
    """
    Loader class for loading the UniversalSpeech.dll library.

    This class provides functionality to check for the existence of
    required DLL files and load the UniversalSpeech.dll library using ctypes.

    Attributes:
        __current_dir (str): The current working directory.
        __dll_files (list): A list of required DLL files.
        __lib_folder (str): The folder name based on the system architecture.

    Methods:
        _files_check(): Checks for the existence of required DLL files.
        load(): Loads the UniversalSpeech.dll library using ctypes.

    Raises:
        DLLFileNotFoundError: Raised if any required DLL file is missing.
    """

    def __init__(self) -> None:
        self.__current_dir = os.path.dirname(os.path.abspath(__file__))
        self.__dll_files = ['dolapi.dll', 'jfwapi.dll', 'nvdaControllerClient.dll', 'SAAPI32.dll', 'UniversalSpeech.dll', 'UniversalSpeech.tlb']
        self.__lib_folder = "lib64" if platform.architecture()[0] == "64bit" else "lib"

    def _files_check(self) -> bool:
        """
        Checks for the existence of required DLL files.

        Returns:
            bool: True if all required DLL files exist, False otherwise.
        """

        lib_folder = os.path.join(self.__current_dir, self.__lib_folder)
        if not os.path.exists(lib_folder):
            return False

        current_dll_files = os.listdir(lib_folder)
        for file in self.__dll_files:
            if file not in current_dll_files:
                return False

        return True

    def load(self) -> object:
        """
        Loads the UniversalSpeech.dll library using ctypes.

        Returns:
            CDLL: The ctypes object representing the loaded library.

        Raises:
            DLLFileNotFoundError: Raised if any required DLL file is missing.
        """

        if not self._files_check():
            raise DLLFileNotFoundError("Missing dll files.")

        # Specify the full path to the DLL
        dll_path = os.path.join(self.__current_dir, self.__lib_folder, "UniversalSpeech.dll")
        uspeech = ctypes.CDLL(dll_path)

        return uspeech
    