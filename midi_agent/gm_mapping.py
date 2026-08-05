"""
GM Instrument mapping and prompt specification parser for MIDI Agent.
Supports Chinese and English instrument names, key/scale definitions, and BPM extraction.
"""

import sys
from pathlib import Path

# Add midi-agent-skill path
SKILL_DIR = Path(__file__).parent.parent / "midi-agent-skill"
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

import re
from typing import Dict, List, Tuple, Optional, Any

# Map Chinese and English terms to GM standard instrument names
INSTRUMENT_TRANSLATIONS: Dict[str, str] = {
    # Piano / Keyboard
    "原声钢琴": "acoustic-grand-piano",
    "钢琴": "acoustic-grand-piano",
    "轻柔钢琴": "acoustic-grand-piano",
    "独奏钢琴": "acoustic-grand-piano",
    "明亮钢琴": "bright-acoustic-piano",
    "电钢琴": "electric-piano-1",
    "羽管键琴": "harpsichord",
    
    # Guitars
    "木吉他": "acoustic-guitar-nylon",
    "尼龙木吉他": "acoustic-guitar-nylon",
    "分解木吉他": "acoustic-guitar-nylon",
    "古典吉他": "acoustic-guitar-nylon",
    "原声吉他": "acoustic-guitar-nylon",
    "民谣吉他": "acoustic-guitar-steel",
    "钢弦吉他": "acoustic-guitar-steel",
    "电吉他": "electric-guitar-clean",
    "失真吉他": "distortion-guitar",
    
    # Bass
    "原声贝斯": "acoustic-bass",
    "低音贝斯": "acoustic-bass",
    "贝斯": "acoustic-bass",
    "电贝斯": "electric-bass-finger",
    "合成贝斯": "synth-bass-1",
    
    # Strings
    "小提琴": "violin",
    "极淡小提琴": "violin",
    "中提琴": "viola",
    "大提琴": "cello",
    "低音提琴": "contrabass",
    "弦乐": "string-ensemble-1",
    "弦乐合奏": "string-ensemble-1",
    "弦乐垫音": "synth-strings-1",
    "微弱弦乐垫音": "synth-strings-1",
    "竖琴": "orchestral-harp",
    
    # Percussion & Bells
    "风铃": "tinkle-bell",
    "微弱风铃": "tinkle-bell",
    "八音盒": "music-box",
    "钢片琴": "celesta",
    "木琴": "xylophone",
    "颤音琴": "vibraphone",
    "马林巴": "marimba",
    
    # Winds & Brass
    "长笛": "flute",
    "短笛": "piccolo",
    "单簧管": "clarinet",
    "双簧管": "oboe",
    "萨克斯": "alto-sax",
    "小号": "trumpet",
    "长号": "trombone",
    "圆号": "french-horn",
    "铜管": "brass-section",
    
    # Synths & Pads
    "合成音色": "lead-1-square",
    "暖音垫": "pad-2-warm",
    "新世纪垫": "pad-1-new-age",
}

# Standard scale note steps (in semitones from root)
SCALE_PATTERNS = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_FLAT_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

def parse_prompt_specs(prompt: str) -> Dict[str, Any]:
    """
    Parses user text prompt to extract explicitly mentioned parameters:
    - bpm (int)
    - key (str, e.g. "C", "G", "A")
    - scale_type (str, e.g. "major", "minor")
    - instruments (list of GM instrument names)
    - no_drums (bool)
    - target_duration_seconds (int)
    - time_signature (str)
    """
    specs: Dict[str, Any] = {
        "bpm": 90,
        "key": "C",
        "scale_type": "major",
        "instruments": [],
        "no_drums": False,
        "target_duration_seconds": 30,
        "time_signature": "4/4",
        "export_format": "midi"  # 'composition', 'midi', or 'wav'
    }
    
    # 1. Parse BPM (e.g. 72BPM, 72 bpm, 120BPM, 速度：72)
    bpm_match = re.search(r'(\d{2,3})\s*(?:BPM|bpm|速度)', prompt)
    if not bpm_match:
        bpm_match = re.search(r'(?:BPM|bpm|速度)[：:]?\s*(\d{2,3})', prompt)
    if bpm_match:
        specs["bpm"] = int(bpm_match.group(1))
        
    # 2. Parse Key & Major/Minor (e.g. C大调, A小调, G Major, D Minor, C调)
    key_match = re.search(r'([A-G][#b]?)\s*(?:大调|小调|Major|Minor|major|minor)', prompt)
    if key_match:
        specs["key"] = key_match.group(1).upper()
        if "小" in key_match.group(0) or "minor" in key_match.group(0).lower():
            specs["scale_type"] = "minor"
        else:
            specs["scale_type"] = "major"
    else:
        # Check simple key mentions like "C调"
        simple_key = re.search(r'([A-G][#b]?)\s*调', prompt)
        if simple_key:
            specs["key"] = simple_key.group(1).upper()

    # 3. Parse Time Signature (e.g., 4/4拍, 3/4拍, 6/8拍)
    time_sig_match = re.search(r'(\d/\d)\s*拍?', prompt)
    if time_sig_match:
        specs["time_signature"] = time_sig_match.group(1)

    # 4. Parse Duration (e.g., 时长60秒, 60秒, 30s, 15 seconds duration, duration 15s)
    dur_match = re.search(r'(?:时长|duration)[：:]?\s*(\d+)\s*(?:秒|s|sec|seconds?)', prompt, re.IGNORECASE)
    if not dur_match:
        dur_match = re.search(r'(\d+)\s*(?:秒|s|sec|seconds?)\s*(?:duration|时长)?', prompt, re.IGNORECASE)
    if dur_match:
        specs["target_duration_seconds"] = int(dur_match.group(1))

    # 5. Check drum requirement (e.g., 不要鼓点, 无鼓点, no drums)
    if re.search(r'(不要鼓点|无鼓点|不需鼓点|no drums)', prompt, re.IGNORECASE):
        specs["no_drums"] = True

    # 6. Parse export format (e.g., 文本格式, composition, wav, binary)
    if re.search(r'(文本格式|composition|text format|JSON)', prompt, re.IGNORECASE):
        specs["export_format"] = "composition"
    elif re.search(r'(wav|WAV|wav file|binary format)', prompt, re.IGNORECASE):
        specs["export_format"] = "wav"
    else:
        specs["export_format"] = "midi"

    # 7. Parse Instruments
    found_instruments = []
    # Check Chinese instrument translations
    for ch_name, gm_name in INSTRUMENT_TRANSLATIONS.items():
        if ch_name in prompt:
            if gm_name not in found_instruments:
                found_instruments.append(gm_name)

    # Check English instruments
    try:
        from midi_types.gm_instruments import GM_INSTRUMENTS, INSTRUMENT_ALIASES
        for eng_alias, gm_name in INSTRUMENT_ALIASES.items():
            pattern = r'\b' + re.escape(eng_alias) + r'\b'
            if re.search(pattern, prompt, re.IGNORECASE):
                if gm_name not in found_instruments:
                    found_instruments.append(gm_name)

        for full_name in GM_INSTRUMENTS.keys():
            if full_name in prompt.lower():
                if full_name not in found_instruments:
                    found_instruments.append(full_name)
    except Exception:
        pass

    if found_instruments:
        specs["instruments"] = found_instruments
    else:
        # Default instruments if none specified
        specs["instruments"] = ["acoustic-grand-piano", "acoustic-guitar-nylon"]

    return specs


def get_scale_pitches(key: str, scale_type: str, octaves: List[int]) -> List[str]:
    """
    Generates pitch names (e.g. ['C4', 'D4', 'E4', ...]) for a given key, scale_type and octaves.
    """
    key = key.upper()
    if key in NOTE_NAMES:
        root_idx = NOTE_NAMES.index(key)
    elif key in NOTE_FLAT_NAMES:
        root_idx = NOTE_FLAT_NAMES.index(key)
    else:
        root_idx = 0  # Default to C

    pattern = SCALE_PATTERNS.get(scale_type, SCALE_PATTERNS["major"])
    scale_pitches = []
    for oct_val in octaves:
        for step in pattern:
            note_idx = (root_idx + step) % 12
            note_name = NOTE_NAMES[note_idx]
            scale_pitches.append(f"{note_name}{oct_val}")

    return scale_pitches
