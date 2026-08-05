"""
Type definitions for music composition.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class Note:
    """A single musical note."""
    pitch: str  # e.g., "C4", "F#5", "Bb3"
    duration: str  # e.g., "4" (quarter), "8" (eighth), "2" (half), "1" (whole)


@dataclass
class Track:
    """A track containing notes for a single instrument."""
    notes: List[Note] = field(default_factory=list)
    instrument: Optional[str] = None  # GM instrument name


@dataclass
class Composition:
    """A complete musical composition."""
    title: str
    bpm: int
    tracks: List[Track] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "bpm": self.bpm,
            "tracks": [
                {
                    "instrument": t.instrument,
                    "notes": [{"pitch": n.pitch, "duration": n.duration} for n in t.notes]
                }
                for t in self.tracks
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Composition":
        """Create from dictionary."""
        tracks = []
        for t in data.get("tracks", []):
            notes = [Note(pitch=n["pitch"], duration=n["duration"]) for n in t.get("notes", [])]
            tracks.append(Track(notes=notes, instrument=t.get("instrument")))

        return cls(
            title=data.get("title", "untitled"),
            bpm=data.get("bpm", 90),
            tracks=tracks
        )
