"""
Voice representation and data structures for UniversalSpeech.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Voice:
    """
    Represents a speech synthesis voice.

    Attributes:
        id (int): Zero-based index of the voice within the engine.
        name (str): Human-readable name of the voice.
        language (Optional[str]): Language/locale code of the voice (e.g. 'en_US', 'ar_SA').
    """
    id: int
    name: str
    language: Optional[str] = None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        if self.language is not None:
            return f"Voice(id={self.id}, name={self.name!r}, language={self.language!r})"
        return f"Voice(id={self.id}, name={self.name!r})"


__all__ = ["Voice"]
