#!/usr/bin/env python3
"""
Normalize and validate composition input.
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from midi_types.music import Composition, Track, Note


def normalize_composition(data: Any) -> Composition:
    """
    Normalize and validate composition input.

    Handles various input formats and ensures a valid Composition object.

    Args:
        data: Raw input data (dict-like)

    Returns:
        A valid Composition object
    """
    if not isinstance(data, dict):
        data = {}

    # Extract title
    title = data.get("title", "untitled")
    if not isinstance(title, str):
        title = str(title) if title else "untitled"

    # Extract BPM
    bpm = data.get("bpm", 90)
    if not isinstance(bpm, (int, float)):
        try:
            bpm = int(bpm)
        except (ValueError, TypeError):
            bpm = 90
    bpm = max(20, min(300, int(bpm)))  # Clamp to reasonable range

    # Extract tracks
    tracks = []
    raw_tracks = data.get("tracks", [])
    if not isinstance(raw_tracks, list):
        raw_tracks = []

    for t in raw_tracks:
        if not isinstance(t, dict):
            continue

        # Extract instrument
        instrument = t.get("instrument")
        if instrument is not None and not isinstance(instrument, str):
            instrument = str(instrument)

        # Extract notes
        notes = []
        raw_notes = t.get("notes", [])
        if not isinstance(raw_notes, list):
            raw_notes = []

        for n in raw_notes:
            if not isinstance(n, dict):
                continue

            pitch = n.get("pitch")
            duration = n.get("duration")

            # Both pitch and duration are required
            if pitch is None or duration is None:
                continue

            notes.append(Note(
                pitch=str(pitch),
                duration=str(duration)
            ))

        if notes:  # Only add tracks with notes
            tracks.append(Track(notes=notes, instrument=instrument))

    return Composition(title=title, bpm=bpm, tracks=tracks)


def normalize_to_dict(data: Any) -> Dict[str, Any]:
    """
    Normalize input and return as dictionary.

    Args:
        data: Raw input data

    Returns:
        Normalized composition as dictionary
    """
    composition = normalize_composition(data)
    return composition.to_dict()


if __name__ == "__main__":
    import json

    # Example with messy input
    messy_input = {
        "title": 123,  # Should become "123"
        "bpm": "120",  # Should become 120
        "tracks": [
            {
                "instrument": "piano",
                "notes": [
                    {"pitch": "C4", "duration": "4"},
                    {"pitch": "E4"},  # Missing duration - should be skipped
                    {"duration": "4"},  # Missing pitch - should be skipped
                    {"pitch": "G4", "duration": "4"}
                ]
            },
            "invalid_track",  # Should be skipped
            {
                "notes": []  # Empty notes - should be skipped
            }
        ]
    }

    result = normalize_composition(messy_input)
    print(json.dumps(result.to_dict(), indent=2))
