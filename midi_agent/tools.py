"""
Tools for the MIDI ADK Agent.
Allows generating MIDI compositions in text format (JSON) or binary format (MIDI/WAV file).
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add paths
ROOT_DIR = Path(__file__).parent.parent
SKILL_DIR = ROOT_DIR / "midi-agent-skill"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from midi_agent.music_generator import create_composition_dict
from skills.generate_midi import generate_midi_from_dict
from skills.convert_to_wav import convert_to_wav, get_conversion_status, ConvertOptions


def ensure_soundfont():
    """Ensure a SoundFont file is placed in soundfonts/A320U.sf2 or available on system."""
    sf_dir = SKILL_DIR / "soundfonts"
    sf_dir.mkdir(parents=True, exist_ok=True)
    target_sf = sf_dir / "A320U.sf2"

    if target_sf.exists():
        return str(target_sf)

    # Check common linux system soundfonts installed by fluid-soundfont-gm
    system_sfs = [
        Path("/usr/share/sounds/sf2/FluidR3_GM.sf2"),
        Path("/usr/share/sounds/sf2/fluid-soundfont-gm.sf2"),
        Path("/usr/share/sounds/sf2/FluidR3_GS.sf2"),
        Path("/usr/share/soundfonts/default.sf2")
    ]
    for sys_sf in system_sfs:
        if sys_sf.exists():
            # Copy or symlink to A320U.sf2
            try:
                import shutil
                shutil.copy(sys_sf, target_sf)
                return str(target_sf)
            except Exception:
                return str(sys_sf)
                
    return str(target_sf)


def generate_composition_text(prompt: str) -> dict:
    """
    Generates music composition in text/JSON format based on the user text prompt.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the structured composition (title, bpm, tracks with instruments and notes).
    """
    composition_dict = create_composition_dict(prompt)
    return {
        "status": "success",
        "format": "composition",
        "composition": composition_dict
    }


from midi_agent.db import save_generation_record


def generate_midi_binary(prompt: str) -> dict:
    """
    Generates music and saves it as a binary MIDI (.mid) file based on the user text prompt.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the status, composition details, file path, and public download URL.
    """
    composition_dict = create_composition_dict(prompt)
    midi_path = generate_midi_from_dict(composition_dict)
    
    file_size = os.path.getsize(midi_path) if os.path.exists(midi_path) else 0
    filename = Path(midi_path).name
    app_url = os.environ.get("APP_URL", "").rstrip("/")
    download_url = f"{app_url}/output/{filename}" if app_url else f"/output/{filename}"

    # Durable persistence to Firestore and private GCS
    try:
        import uuid, datetime
        gen_id = str(uuid.uuid4())[:8]
        record = {
            "id": gen_id,
            "prompt": prompt,
            "format": "midi",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "composition": composition_dict,
            "midi_url": f"/output/{filename}",
            "wav_url": None
        }
        save_generation_record(record)
    except Exception as e:
        print(f"Warning: Failed to save record to storage: {e}")

    return {
        "status": "success",
        "format": "midi",
        "file_name": filename,
        "file_path": midi_path,
        "download_url": download_url,
        "file_size_bytes": file_size,
        "bpm": composition_dict.get("bpm"),
        "title": composition_dict.get("title"),
        "track_count": len(composition_dict.get("tracks", []))
    }


def generate_wav_binary(prompt: str) -> dict:
    """
    Generates music and converts it to a binary WAV (.wav) audio file based on the user text prompt.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the status, composition details, file path, and public download URLs for WAV and MIDI.
    """
    composition_dict = create_composition_dict(prompt)
    midi_path = generate_midi_from_dict(composition_dict)
    
    sf_path = ensure_soundfont()
    options = ConvertOptions(soundfont_path=sf_path if os.path.exists(sf_path) else None)
    
    wav_path = convert_to_wav(midi_path, options=options)
    file_size = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0
    filename = Path(wav_path).name
    midi_filename = Path(midi_path).name
    app_url = os.environ.get("APP_URL", "").rstrip("/")
    download_url = f"{app_url}/output/{filename}" if app_url else f"/output/{filename}"
    midi_download_url = f"{app_url}/output/{midi_filename}" if app_url else f"/output/{midi_filename}"

    # Durable persistence to Firestore and private GCS
    try:
        import uuid, datetime
        gen_id = str(uuid.uuid4())[:8]
        record = {
            "id": gen_id,
            "prompt": prompt,
            "format": "wav",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "composition": composition_dict,
            "midi_url": f"/output/{midi_filename}",
            "wav_url": f"/output/{filename}"
        }
        save_generation_record(record)
    except Exception as e:
        print(f"Warning: Failed to save record to storage: {e}")

    return {
        "status": "success",
        "format": "wav",
        "file_name": filename,
        "file_path": wav_path,
        "download_url": download_url,
        "midi_download_url": midi_download_url,
        "file_size_bytes": file_size,
        "bpm": composition_dict.get("bpm"),
        "title": composition_dict.get("title"),
        "track_count": len(composition_dict.get("tracks", []))
    }


def generate_music(prompt: str, output_format: str = "composition") -> dict:
    """
    Generate MIDI music in the specified output format given a user prompt.

    Args:
        prompt: User music prompt (English or Chinese).
        output_format: Desired format - 'composition' (text/JSON), 'midi' (binary MIDI file), 'wav' (binary audio WAV file), or 'all'.

    Returns:
        dict containing generated output results.
    """
    fmt = output_format.lower().strip()
    if fmt == "wav":
        return generate_wav_binary(prompt)
    elif fmt == "midi":
        return generate_midi_binary(prompt)
    elif fmt == "all":
        comp_res = generate_composition_text(prompt)
        midi_res = generate_midi_binary(prompt)
        wav_res = generate_wav_binary(prompt)
        return {
            "status": "success",
            "format": "all",
            "composition": comp_res["composition"],
            "midi_file": midi_res["file_path"],
            "wav_file": wav_res["file_path"]
        }
    else:
        return generate_composition_text(prompt)
