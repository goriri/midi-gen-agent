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


def get_public_base_url() -> str:
    """ Resolves the public base URL of the running Cloud Run service or local server. """
    url = os.environ.get("DYNAMIC_APP_URL") or os.environ.get("APP_URL")
    if url:
        return url.rstrip("/")

    # Fallback: If running on Cloud Run (K_SERVICE set), attempt self-discovery via Metadata + Cloud Run v2 API
    k_service = os.environ.get("K_SERVICE")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
    region = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    if k_service and project:
        try:
            import urllib.request
            meta_req = urllib.request.Request(
                "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
                headers={"Metadata-Flavor": "Google"}
            )
            with urllib.request.urlopen(meta_req, timeout=3) as resp:
                token = json.loads(resp.read().decode("utf-8")).get("access_token")
            if token:
                run_url = f"https://run.googleapis.com/v2/projects/{project}/locations/{region}/services/{k_service}"
                api_req = urllib.request.Request(run_url, headers={"Authorization": f"Bearer {token}"})
                with urllib.request.urlopen(api_req, timeout=5) as resp:
                    svc_data = json.loads(resp.read().decode("utf-8"))
                    uri = svc_data.get("uri")
                    if uri:
                        os.environ["DYNAMIC_APP_URL"] = uri.rstrip("/")
                        return uri.rstrip("/")
        except Exception as e:
            print(f"Cloud Run URL auto-discovery warning: {e}")

    return "http://localhost:8000"


from midi_agent.db import save_generation_record, GCS_BUCKET_NAME


def _select_accessible_urls(wav_filename: str, midi_filename: str, base_url: str, bucket_name: str) -> tuple[str, str, str, str]:
    """
    Determines the best accessible download URLs for browser users.
    If Cloud Run unauthenticated access (allUsers) is blocked by GCP Organization Policy
    (returning 403 Forbidden on /output/...), automatically falls back to Google Cloud Storage
    cookie-authenticated browser URLs (https://storage.cloud.google.com/<bucket>/output/<file>).
    """
    cloud_run_wav = f"{base_url}/output/{wav_filename}"
    cloud_run_midi = f"{base_url}/output/{midi_filename}"
    gcs_auth_wav = f"https://storage.cloud.google.com/{bucket_name}/output/{wav_filename}"
    gcs_auth_midi = f"https://storage.cloud.google.com/{bucket_name}/output/{midi_filename}"

    if "localhost" in base_url or "127.0.0.1" in base_url:
        return cloud_run_wav, cloud_run_midi, gcs_auth_wav, gcs_auth_midi

    try:
        import urllib.request
        req = urllib.request.Request(cloud_run_wav, method="HEAD")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status == 200:
                return cloud_run_wav, cloud_run_midi, gcs_auth_wav, gcs_auth_midi
    except Exception as e:
        print(f"Cloud Run unauthenticated probe returned non-200 ({e}); using storage.cloud.google.com authenticated URLs.")

    return gcs_auth_wav, gcs_auth_midi, gcs_auth_wav, gcs_auth_midi


def _render_and_persist_all(prompt: str, fmt: str = "all") -> dict:
    """
    Core helper that generates composition JSON, binary MIDI (.mid), and synthesized WAV (.wav)
    in a single pass, persists to Firestore + GCS, and returns verified download URLs.
    """
    composition_dict = create_composition_dict(prompt)
    midi_path = generate_midi_from_dict(composition_dict)

    sf_path = ensure_soundfont()
    options = ConvertOptions(soundfont_path=sf_path if os.path.exists(sf_path) else None)
    wav_path = convert_to_wav(midi_path, options=options)

    midi_filename = Path(midi_path).name
    wav_filename = Path(wav_path).name
    wav_size = os.path.getsize(wav_path) if os.path.exists(wav_path) else 0
    midi_size = os.path.getsize(midi_path) if os.path.exists(midi_path) else 0

    # Durable persistence to Firestore and GCS first so files exist in GCS bucket
    try:
        import uuid, datetime
        gen_id = str(uuid.uuid4())[:8]
        record = {
            "id": gen_id,
            "prompt": prompt,
            "format": fmt,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "composition": composition_dict,
            "midi_url": f"/output/{midi_filename}",
            "wav_url": f"/output/{wav_filename}"
        }
        save_generation_record(record)
    except Exception as e:
        print(f"Warning: Failed to save record to storage: {e}")

    base_url = get_public_base_url()
    wav_download_url, midi_download_url, gcs_auth_wav, gcs_auth_midi = _select_accessible_urls(
        wav_filename, midi_filename, base_url, GCS_BUCKET_NAME
    )
    primary_download_url = midi_download_url if fmt == "midi" else wav_download_url

    return {
        "status": "success",
        "format": fmt,
        "title": composition_dict.get("title"),
        "bpm": composition_dict.get("bpm"),
        "track_count": len(composition_dict.get("tracks", [])),
        "actual_duration_seconds": composition_dict.get("actual_duration_seconds"),
        "composition": composition_dict,
        "file_name": midi_filename if fmt == "midi" else wav_filename,
        "file_path": midi_path if fmt == "midi" else wav_path,
        "midi_file": midi_path,
        "wav_file": wav_path,
        "file_size_bytes": midi_size if fmt == "midi" else wav_size,
        "download_url": primary_download_url,
        "wav_download_url": wav_download_url,
        "midi_download_url": midi_download_url,
        "gcs_authenticated_wav_url": gcs_auth_wav,
        "gcs_authenticated_midi_url": gcs_auth_midi,
    }


def generate_composition_text(prompt: str) -> dict:
    """
    Generates music composition in text/JSON format along with downloadable MIDI and WAV links.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the structured composition and public download URLs for WAV and MIDI.
    """
    return _render_and_persist_all(prompt, fmt="composition")


def generate_midi_binary(prompt: str) -> dict:
    """
    Generates music and saves it as a binary MIDI (.mid) file based on the user text prompt.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the status, composition details, file path, and public download URLs.
    """
    return _render_and_persist_all(prompt, fmt="midi")


def generate_wav_binary(prompt: str) -> dict:
    """
    Generates music and converts it to a binary WAV (.wav) audio file based on the user text prompt.

    Args:
        prompt: User music generation prompt specifying style, BPM, key, instruments, etc.

    Returns:
        dict containing the status, composition details, file path, and public download URLs for WAV and MIDI.
    """
    return _render_and_persist_all(prompt, fmt="wav")


def generate_music(prompt: str, output_format: str = "all") -> dict:
    """
    Generate MIDI music in the specified output format given a user prompt.

    Args:
        prompt: User music prompt (English or Chinese).
        output_format: Desired format - 'all' (default, generates composition + MIDI + WAV), 'wav', 'midi', or 'composition'.

    Returns:
        dict containing generated output results including wav_download_url and midi_download_url.
    """
    fmt = (output_format or "all").lower().strip()
    return _render_and_persist_all(prompt, fmt=fmt)
