#!/usr/bin/env python3
"""
Refine composition by adjusting length and other properties.
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from midi_types.music import Composition, Track, Note


def refine_composition(composition: Composition, min_notes: int = 16) -> Composition:
    """
    Refine a composition by ensuring minimum note count per track.

    If a track has fewer notes than min_notes, the existing notes are
    repeated to reach the minimum.

    Args:
        composition: The composition to refine
        min_notes: Minimum number of notes per track (default: 16)

    Returns:
        Refined composition
    """
    for track in composition.tracks:
        if 0 < len(track.notes) < min_notes:
            base = list(track.notes)  # Copy original notes
            while len(track.notes) < min_notes:
                for note in base:
                    if len(track.notes) >= min_notes:
                        break
                    track.notes.append(Note(pitch=note.pitch, duration=note.duration))

    return composition


def refine_from_dict(data: Dict[str, Any], min_notes: int = 16) -> Dict[str, Any]:
    """
    Refine a composition from dictionary input.

    Args:
        data: Composition as dictionary
        min_notes: Minimum number of notes per track

    Returns:
        Refined composition as dictionary
    """
    composition = Composition.from_dict(data)
    refined = refine_composition(composition, min_notes)
    return refined.to_dict()


def extend_composition(composition: Composition, target_bars: int = 8, beats_per_bar: int = 4) -> Composition:
    """
    Extend composition to reach a target number of bars.

    Args:
        composition: The composition to extend
        target_bars: Target number of bars
        beats_per_bar: Beats per bar (time signature numerator)

    Returns:
        Extended composition
    """
    target_beats = target_bars * beats_per_bar

    for track in composition.tracks:
        if not track.notes:
            continue

        # Calculate current duration
        current_beats = sum(_duration_to_beats(n.duration) for n in track.notes)

        if current_beats >= target_beats:
            continue

        # Repeat notes to fill target duration
        base = list(track.notes)
        base_beats = current_beats

        while current_beats < target_beats:
            for note in base:
                if current_beats >= target_beats:
                    break
                track.notes.append(Note(pitch=note.pitch, duration=note.duration))
                current_beats += _duration_to_beats(note.duration)

    return composition


def _duration_to_beats(duration_str: str) -> float:
    """Convert duration string to beats."""
    duration_map = {
        "1": 4.0, "2": 2.0, "d2": 3.0, "4": 1.0, "d4": 1.5,
        "8": 0.5, "d8": 0.75, "16": 0.25, "32": 0.125
    }

    if duration_str in duration_map:
        return duration_map[duration_str]

    try:
        division = float(duration_str)
        if division > 0:
            return 4.0 / division
    except ValueError:
        pass

    return 1.0


if __name__ == "__main__":
    import json

    # Example with short tracks
    short_composition = {
        "title": "Short Song",
        "bpm": 100,
        "tracks": [
            {
                "instrument": "piano",
                "notes": [
                    {"pitch": "C4", "duration": "4"},
                    {"pitch": "E4", "duration": "4"},
                    {"pitch": "G4", "duration": "4"}
                ]
            },
            {
                "instrument": "bass",
                "notes": [
                    {"pitch": "C2", "duration": "2"}
                ]
            }
        ]
    }

    result = refine_from_dict(short_composition, min_notes=8)
    print(json.dumps(result, indent=2))
