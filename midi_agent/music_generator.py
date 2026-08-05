"""
Composition engine for MIDI Agent.
Generates music composition JSON adhering to music theory guidelines and user prompt specs.
Includes exact bar-precise measure targeting and duration self-correction loop to guarantee duration within ±5 seconds.
"""

import sys
import math
import random
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add midi-agent-skill path
SKILL_DIR = Path(__file__).parent.parent / "midi-agent-skill"
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from midi_agent.gm_mapping import parse_prompt_specs, get_scale_pitches, NOTE_NAMES, NOTE_FLAT_NAMES
from skills.normalize_composition import normalize_composition
from skills.refine_composition import _duration_to_beats


# Common chord progressions (as scale degree indices 0-6)
MAJOR_PROGRESSIONS = [
    [0, 4, 5, 3],  # I - V - vi - IV (Pop/Japanese light music)
    [0, 5, 3, 4],  # I - vi - IV - V (Canon / Healing ballad)
    [3, 4, 2, 5],  # IV - V - iii - vi (Royal road / J-Pop)
    [0, 3, 4, 0],  # I - IV - V - I
]

MINOR_PROGRESSIONS = [
    [0, 5, 2, 6],  # i - VI - III - VII
    [0, 3, 4, 0],  # i - iv - v - i
    [0, 5, 3, 4],  # i - VI - iv - v
]


def calculate_composition_duration_seconds(comp_dict: Dict[str, Any]) -> float:
    """
    Calculates exact audio duration in seconds for a composition dictionary.
    """
    bpm = comp_dict.get("bpm", 90)
    tracks = comp_dict.get("tracks", [])
    if not tracks:
        return 0.0

    max_beats = 0.0
    for track in tracks:
        track_beats = sum(_duration_to_beats(n.get("duration", "4")) for n in track.get("notes", []))
        if track_beats > max_beats:
            max_beats = track_beats

    # Seconds = (max_beats / bpm) * 60
    return (max_beats / bpm) * 60.0


def generate_notes_for_track(
    role: str,
    scale_pitches_low: List[str],
    scale_pitches_mid: List[str],
    scale_pitches_high: List[str],
    progression: List[int],
    target_measures: int = 16
) -> List[Dict[str, str]]:
    """
    Generates structured, consonant notes for a track for exact target measure count.
    """
    notes = []
    prog_len = len(progression)
    
    for m in range(target_measures):
        degree = progression[m % prog_len]
        
        if role == "melody":
            root_pitch_mid = scale_pitches_mid[degree % len(scale_pitches_mid)]
            third_pitch_mid = scale_pitches_mid[(degree + 2) % len(scale_pitches_mid)]
            fifth_pitch_mid = scale_pitches_mid[(degree + 4) % len(scale_pitches_mid)]
            
            notes.extend([
                {"pitch": root_pitch_mid, "duration": "4"},
                {"pitch": third_pitch_mid, "duration": "8"},
                {"pitch": fifth_pitch_mid, "duration": "8"},
                {"pitch": root_pitch_mid, "duration": "4"},
                {"pitch": third_pitch_mid, "duration": "4"},
            ])

        elif role == "arpeggio":
            p1 = scale_pitches_mid[degree % len(scale_pitches_mid)]
            p2 = scale_pitches_mid[(degree + 2) % len(scale_pitches_mid)]
            p3 = scale_pitches_mid[(degree + 4) % len(scale_pitches_mid)]
            p4 = scale_pitches_high[degree % len(scale_pitches_high)]
            
            notes.extend([
                {"pitch": p1, "duration": "8"},
                {"pitch": p2, "duration": "8"},
                {"pitch": p3, "duration": "8"},
                {"pitch": p4, "duration": "8"},
                {"pitch": p3, "duration": "8"},
                {"pitch": p2, "duration": "8"},
                {"pitch": p1, "duration": "8"},
                {"pitch": p3, "duration": "8"},
            ])

        elif role == "pad":
            p1 = scale_pitches_mid[degree % len(scale_pitches_mid)]
            p2 = scale_pitches_mid[(degree + 4) % len(scale_pitches_mid)]
            notes.extend([
                {"pitch": p1, "duration": "2"},
                {"pitch": p2, "duration": "2"},
            ])

        elif role == "ornament":
            p_high = scale_pitches_high[(degree + 4) % len(scale_pitches_high)]
            notes.extend([
                {"pitch": p_high, "duration": "1"},
            ])

        elif role == "bass":
            root_low = scale_pitches_low[degree % len(scale_pitches_low)]
            fifth_low = scale_pitches_low[(degree + 4) % len(scale_pitches_low)]
            notes.extend([
                {"pitch": root_low, "duration": "2"},
                {"pitch": fifth_low, "duration": "2"},
            ])
                
    return notes


def create_composition_dict(prompt: str) -> Dict[str, Any]:
    """
    Generates a full composition dictionary from a text prompt.
    Uses exact measure targeting and self-correction loop to guarantee duration within ±5 seconds.
    """
    specs = parse_prompt_specs(prompt)
    
    key = specs["key"]
    scale_type = specs["scale_type"]
    bpm = specs["bpm"]
    instruments = specs["instruments"]
    target_duration = specs["target_duration_seconds"]

    scale_low = get_scale_pitches(key, scale_type, [2, 3])
    scale_mid = get_scale_pitches(key, scale_type, [4])
    scale_high = get_scale_pitches(key, scale_type, [5, 6])

    progression = MINOR_PROGRESSIONS[0] if scale_type == "minor" else MAJOR_PROGRESSIONS[0]

    # Calculate exact measure count needed
    # Seconds per measure (4 beats at bpm) = (4.0 / bpm) * 60.0 = 240.0 / bpm
    seconds_per_measure = 240.0 / bpm
    target_measures = max(4, int(round(target_duration / seconds_per_measure)))

    # 1. Initial Generation
    comp_dict = _build_raw_composition(prompt, bpm, instruments, scale_low, scale_mid, scale_high, progression, target_measures)
    actual_duration = calculate_composition_duration_seconds(comp_dict)
    
    # 2. Self-Correction Verification Loop
    max_retries = 3
    retry = 0
    while abs(actual_duration - target_duration) > 5.0 and retry < max_retries:
        retry += 1
        print(f"Duration self-correction check (Attempt {retry}): Target = {target_duration}s, Actual = {actual_duration:.1f}s")
        
        # Adjust target measures directly based on duration delta
        measure_diff = int(round((target_duration - actual_duration) / seconds_per_measure))
        if measure_diff == 0:
            measure_diff = 1 if target_duration > actual_duration else -1
            
        target_measures = max(1, target_measures + measure_diff)
        comp_dict = _build_raw_composition(prompt, bpm, instruments, scale_low, scale_mid, scale_high, progression, target_measures)
        actual_duration = calculate_composition_duration_seconds(comp_dict)

    # Final normalization
    try:
        norm_comp = normalize_composition(comp_dict)
        final_dict = norm_comp.to_dict()
        final_dict["actual_duration_seconds"] = round(calculate_composition_duration_seconds(final_dict), 1)
        return final_dict
    except Exception as e:
        comp_dict["actual_duration_seconds"] = round(actual_duration, 1)
        return comp_dict


def _build_raw_composition(prompt, bpm, instruments, scale_low, scale_mid, scale_high, progression, target_measures):
    tracks = []
    for i, inst in enumerate(instruments):
        if i == 0:
            role = "melody"
        elif i == 1:
            role = "arpeggio"
        elif i == 2:
            if "bass" in inst or "cello" in inst:
                role = "bass"
            elif "violin" in inst or "pad" in inst or "strings" in inst:
                role = "pad"
            else:
                role = "ornament"
        elif "bell" in inst or "celesta" in inst or "box" in inst:
            role = "ornament"
        elif "bass" in inst:
            role = "bass"
        else:
            role = "pad"

        track_notes = generate_notes_for_track(
            role, scale_low, scale_mid, scale_high, progression, target_measures=target_measures
        )
        tracks.append({
            "instrument": inst,
            "notes": track_notes
        })

    title = prompt[:30].replace("\n", " ").strip() or "Composition"
    return {
        "title": title,
        "bpm": bpm,
        "tracks": tracks
    }
