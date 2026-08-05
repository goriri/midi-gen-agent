"""
Durable database and Cloud Storage manager for MIDI Agent.
Uses Google Cloud Firestore for metadata JSON and a PRIVATE Google Cloud Storage (GCS) bucket for WAV/MIDI binary files.
Supports local JSON filesystem fallback for offline development.
"""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

GCP_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "cellular-cider-495602-r9")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "cellular-cider-495602-r9-midi-studio")
COLLECTION_NAME = "generations"

# Fallback local paths
STORAGE_DIR = Path(__file__).parent.parent / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_HISTORY_FILE = STORAGE_DIR / "generations.json"

# Initialize GCP clients
_firestore_db = None
_storage_bucket = None

try:
    from google.cloud import firestore
    from google.cloud import storage

    _firestore_db = firestore.Client(project=GCP_PROJECT)
    _storage_client = storage.Client(project=GCP_PROJECT)
    _storage_bucket = _storage_client.bucket(GCS_BUCKET_NAME)
    print(f"Durable Private Storage Initialized: Firestore + Private GCS ({GCS_BUCKET_NAME})")
except Exception as e:
    print(f"Cloud Storage fallback to local filesystem: {e}")


def upload_file_to_gcs(local_file_path: str) -> Optional[str]:
    """Uploads a binary file to private GCS bucket."""
    if not _storage_bucket or not os.path.exists(local_file_path):
        return None

    try:
        filename = Path(local_file_path).name
        blob = _storage_bucket.blob(f"output/{filename}")
        blob.upload_from_filename(local_file_path)
        print(f"Uploaded {filename} to private GCS bucket {GCS_BUCKET_NAME}")
        return f"/output/{filename}"
    except Exception as e:
        print(f"Error uploading to private GCS: {e}")
        return None


def download_file_from_gcs(filename: str, destination_path: str) -> bool:
    """Downloads a binary file from private GCS bucket if not present locally."""
    if not _storage_bucket:
        return False
    try:
        blob = _storage_bucket.blob(f"output/{filename}")
        if blob.exists():
            blob.download_to_filename(destination_path)
            print(f"Downloaded {filename} from private GCS to {destination_path}")
            return True
    except Exception as e:
        print(f"Error downloading from private GCS: {e}")
    return False


def save_generation_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves generation record to Firestore (and uploads binary audio to private GCS) with local backup.
    Preserves relative /output/{filename} endpoint URLs so frontend streams via server proxy.
    """
    gen_id = record.get("id")
    if not gen_id:
        return record

    output_dir = Path(__file__).parent.parent / "midi-agent-skill" / "output"
    
    if record.get("wav_url") and record["wav_url"].startswith("/output/"):
        wav_filename = record["wav_url"].replace("/output/", "")
        local_wav = output_dir / wav_filename
        if local_wav.exists():
            upload_file_to_gcs(str(local_wav))

    if record.get("midi_url") and record["midi_url"].startswith("/output/"):
        midi_filename = record["midi_url"].replace("/output/", "")
        local_midi = output_dir / midi_filename
        if local_midi.exists():
            upload_file_to_gcs(str(local_midi))

    # Save to Firestore
    if _firestore_db:
        try:
            doc_ref = _firestore_db.collection(COLLECTION_NAME).document(gen_id)
            doc_ref.set(record)
            print(f"Saved generation #{gen_id} to Firestore")
        except Exception as e:
            print(f"Firestore save error: {e}")

    # Local file backup
    save_local_history_backup(record)
    return record


def get_all_generations() -> List[Dict[str, Any]]:
    """
    Retrieves all generation records from Firestore (or local backup).
    """
    records = []
    if _firestore_db:
        try:
            docs = _firestore_db.collection(COLLECTION_NAME).order_by(
                "created_at", direction=firestore.Query.DESCENDING
            ).limit(50).stream()
            for doc in docs:
                records.append(doc.to_dict())
            if records:
                return records
        except Exception as e:
            print(f"Firestore query error: {e}")

    # Fallback to local history
    return load_local_history_backup()


def load_local_history_backup() -> List[Dict[str, Any]]:
    if LOCAL_HISTORY_FILE.exists():
        try:
            with open(LOCAL_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_local_history_backup(record: Dict[str, Any]):
    history = load_local_history_backup()
    # Replace existing or append
    history = [h for h in history if h.get("id") != record.get("id")]
    history.append(record)
    with open(LOCAL_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
