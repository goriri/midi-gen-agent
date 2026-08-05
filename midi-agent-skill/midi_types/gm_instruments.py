"""
General MIDI Instrument List (Program Change 0-127)
Compatible with A320U.sf2 SoundFont
Reference: https://soundprogramming.net/file-formats/general-midi-instrument-list/
"""

from typing import Dict, List, Optional

GM_INSTRUMENTS: Dict[str, int] = {
    # Piano (0-7)
    "acoustic-grand-piano": 0,
    "bright-acoustic-piano": 1,
    "electric-grand-piano": 2,
    "honky-tonk-piano": 3,
    "electric-piano-1": 4,
    "electric-piano-2": 5,
    "harpsichord": 6,
    "clavinet": 7,

    # Chromatic Percussion (8-15)
    "celesta": 8,
    "glockenspiel": 9,
    "music-box": 10,
    "vibraphone": 11,
    "marimba": 12,
    "xylophone": 13,
    "tubular-bells": 14,
    "dulcimer": 15,

    # Organ (16-23)
    "drawbar-organ": 16,
    "percussive-organ": 17,
    "rock-organ": 18,
    "church-organ": 19,
    "reed-organ": 20,
    "accordion": 21,
    "harmonica": 22,
    "tango-accordion": 23,

    # Guitar (24-31)
    "acoustic-guitar-nylon": 24,
    "acoustic-guitar-steel": 25,
    "electric-guitar-jazz": 26,
    "electric-guitar-clean": 27,
    "electric-guitar-muted": 28,
    "overdriven-guitar": 29,
    "distortion-guitar": 30,
    "guitar-harmonics": 31,

    # Bass (32-39)
    "acoustic-bass": 32,
    "electric-bass-finger": 33,
    "electric-bass-pick": 34,
    "fretless-bass": 35,
    "slap-bass-1": 36,
    "slap-bass-2": 37,
    "synth-bass-1": 38,
    "synth-bass-2": 39,

    # Strings (40-47)
    "violin": 40,
    "viola": 41,
    "cello": 42,
    "contrabass": 43,
    "tremolo-strings": 44,
    "pizzicato-strings": 45,
    "orchestral-harp": 46,
    "timpani": 47,

    # Ensemble (48-55)
    "string-ensemble-1": 48,
    "string-ensemble-2": 49,
    "synth-strings-1": 50,
    "synth-strings-2": 51,
    "choir-aahs": 52,
    "voice-oohs": 53,
    "synth-voice": 54,
    "orchestra-hit": 55,

    # Brass (56-63)
    "trumpet": 56,
    "trombone": 57,
    "tuba": 58,
    "muted-trumpet": 59,
    "french-horn": 60,
    "brass-section": 61,
    "synth-brass-1": 62,
    "synth-brass-2": 63,

    # Reed (64-71)
    "soprano-sax": 64,
    "alto-sax": 65,
    "tenor-sax": 66,
    "baritone-sax": 67,
    "oboe": 68,
    "english-horn": 69,
    "bassoon": 70,
    "clarinet": 71,

    # Pipe (72-79)
    "piccolo": 72,
    "flute": 73,
    "recorder": 74,
    "pan-flute": 75,
    "blown-bottle": 76,
    "shakuhachi": 77,
    "whistle": 78,
    "ocarina": 79,

    # Synth Lead (80-87)
    "lead-1-square": 80,
    "lead-2-sawtooth": 81,
    "lead-3-calliope": 82,
    "lead-4-chiff": 83,
    "lead-5-charang": 84,
    "lead-6-voice": 85,
    "lead-7-fifths": 86,
    "lead-8-bass-lead": 87,

    # Synth Pad (88-95)
    "pad-1-new-age": 88,
    "pad-2-warm": 89,
    "pad-3-polysynth": 90,
    "pad-4-choir": 91,
    "pad-5-bowed": 92,
    "pad-6-metallic": 93,
    "pad-7-halo": 94,
    "pad-8-sweep": 95,

    # Synth Effects (96-103)
    "fx-1-rain": 96,
    "fx-2-soundtrack": 97,
    "fx-3-crystal": 98,
    "fx-4-atmosphere": 99,
    "fx-5-brightness": 100,
    "fx-6-goblins": 101,
    "fx-7-echoes": 102,
    "fx-8-sci-fi": 103,

    # Ethnic (104-111)
    "sitar": 104,
    "banjo": 105,
    "shamisen": 106,
    "koto": 107,
    "kalimba": 108,
    "bagpipe": 109,
    "fiddle": 110,
    "shanai": 111,

    # Percussive (112-119)
    "tinkle-bell": 112,
    "agogo": 113,
    "steel-drums": 114,
    "woodblock": 115,
    "taiko-drum": 116,
    "melodic-tom": 117,
    "synth-drum": 118,
    "reverse-cymbal": 119,

    # Sound Effects (120-127)
    "guitar-fret-noise": 120,
    "breath-noise": 121,
    "seashore": 122,
    "bird-tweet": 123,
    "telephone-ring": 124,
    "helicopter": 125,
    "applause": 126,
    "gunshot": 127
}

INSTRUMENT_ALIASES: Dict[str, str] = {
    "piano": "acoustic-grand-piano",
    "grand-piano": "acoustic-grand-piano",
    "electric-piano": "electric-piano-1",
    "rhodes": "electric-piano-1",
    "organ": "drawbar-organ",
    "hammond": "drawbar-organ",
    "guitar": "acoustic-guitar-nylon",
    "nylon-guitar": "acoustic-guitar-nylon",
    "steel-guitar": "acoustic-guitar-steel",
    "clean-guitar": "electric-guitar-clean",
    "distorted-guitar": "distortion-guitar",
    "bass": "acoustic-bass",
    "electric-bass": "electric-bass-finger",
    "synth-bass": "synth-bass-1",
    "strings": "string-ensemble-1",
    "orchestra-strings": "string-ensemble-1",
    "choir": "choir-aahs",
    "vocals": "choir-aahs",
    "sax": "alto-sax",
    "saxophone": "alto-sax",
    "brass": "brass-section",
    "horns": "brass-section",
    "synth-lead": "lead-1-square",
    "synth-pad": "pad-1-new-age",
    "drums": "synth-drum",
    "harp": "orchestral-harp"
}


def resolve_instrument(name: str) -> int:
    """
    Resolve instrument name to GM program number.

    Args:
        name: Instrument name (can be alias or full name)

    Returns:
        Program number (0-127) or 0 (piano) if not found
    """
    import re
    normalized = re.sub(r'[\s_]+', '-', name.lower())

    # Check direct match
    if normalized in GM_INSTRUMENTS:
        return GM_INSTRUMENTS[normalized]

    # Check alias
    if normalized in INSTRUMENT_ALIASES:
        return GM_INSTRUMENTS[INSTRUMENT_ALIASES[normalized]]

    # Fuzzy match: find instrument containing the name
    for key, value in GM_INSTRUMENTS.items():
        if normalized in key or key.replace('-', '') in normalized:
            return value

    # Default to piano
    return 0


def get_instrument_name(program_number: int) -> str:
    """Get instrument name from program number."""
    for name, num in GM_INSTRUMENTS.items():
        if num == program_number:
            return name
    return "acoustic-grand-piano"


def get_instruments_by_category(category: str) -> List[str]:
    """Get list of instruments by category."""
    categories: Dict[str, tuple] = {
        "piano": (0, 7),
        "chromatic-percussion": (8, 15),
        "organ": (16, 23),
        "guitar": (24, 31),
        "bass": (32, 39),
        "strings": (40, 47),
        "ensemble": (48, 55),
        "brass": (56, 63),
        "reed": (64, 71),
        "pipe": (72, 79),
        "synth-lead": (80, 87),
        "synth-pad": (88, 95),
        "synth-effects": (96, 103),
        "ethnic": (104, 111),
        "percussive": (112, 119),
        "sound-effects": (120, 127)
    }

    range_tuple = categories.get(category.lower())
    if not range_tuple:
        return []

    return [
        name for name, num in GM_INSTRUMENTS.items()
        if range_tuple[0] <= num <= range_tuple[1]
    ]
