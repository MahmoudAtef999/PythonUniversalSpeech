"""
Voice representation and data structures for UniversalSpeech.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Voice:
    """
    Represents a speech synthesis voice.

    Attributes:
        id (int): Zero-based index of the voice within the engine.
        name (str): Human-readable name of the voice.
    """
    id: int
    name: str

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Voice(id={self.id}, name={self.name!r})"


__all__ = ["Voice"]
