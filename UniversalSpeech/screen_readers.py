"""
Screen reader inquiry and status representations for UniversalSpeech.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ScreenReaderInfo:
    """
    Represents information about a screen reader engine supported by UniversalSpeech.

    Attributes:
        id (int): Zero-based integer ID of the screen reader.
        name (str): The display name of the screen reader (e.g. 'NVDA', 'Jaws', 'SAPI5').
        available (bool): True if the screen reader is currently running/available.
    """
    id: int
    name: str
    available: bool

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"ScreenReaderInfo(id={self.id}, name={self.name!r}, available={self.available})"


__all__ = ["ScreenReaderInfo"]
