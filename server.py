"""
FastAPI Server for ADK MIDI Agent Modern Web Frontend.
Provides REST API endpoints for music generation, composition to WAV conversion,
and durable cloud generation history using Firestore and PRIVATE Cloud Storage.
"""

import os
import sys
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add paths
ROOT_DIR = Path(__file__).parent
SKILL_DIR = ROOT_DIR / "midi-agent-skill"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import contextlib
from midi_agent.tools import generate_music, ensure_soundfont
from midi_agent.db import save_generation_record, get_all_generations, download_file_from_gcs
from skills.generate_midi import generate_midi_from_dict
from skills.convert_to_wav import convert_to_wav, ConvertOptions


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Mount A2A (Agent-to-Agent) routes dynamically for Gemini Enterprise and A2A clients."""
    try:
        from a2a.server.tasks import InMemoryTaskStore
        from a2a.server.apps import A2AFastAPIApplication
        from a2a.server.request_handlers import DefaultRequestHandler
        from a2a.types import AgentCapabilities
        from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
        from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from midi_agent.agent import root_agent

        session_service = InMemorySessionService()
        runner = Runner(agent=root_agent, app_name="app", session_service=session_service, auto_create_session=True)
        app.state.runner = runner

        app_url = os.environ.get("APP_URL", "http://0.0.0.0:8080").rstrip("/")
        card = await AgentCardBuilder(
            agent=root_agent,
            capabilities=AgentCapabilities(streaming=True),
            rpc_url=f"{app_url}/a2a/app",
            agent_version="0.1.0"
        ).build()

        handler = DefaultRequestHandler(
            agent_executor=A2aAgentExecutor(runner=runner),
            task_store=InMemoryTaskStore()
        )
        a2a_app = A2AFastAPIApplication(agent_card=card, http_handler=handler)
        a2a_app.add_routes_to_app(app, agent_card_url="/a2a/app/.well-known/agent-card.json", rpc_url="/a2a/app")
        print("[A2A] Mounted A2A protocol routes and agent-card endpoint at /a2a/app")
    except Exception as e:
        print(f"[A2A] Warning: Could not initialize A2A routes: {e}")

    yield


app = FastAPI(title="ADK MIDI Agent Web UI", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def capture_request_base_url(request: Request, call_next):
    """Automatically captures the live public Cloud Run / host URL on every request."""
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    proto = request.headers.get("x-forwarded-proto", "https")
    if host and not host.startswith(("localhost", "127.0.0.1", "0.0.0.0")):
        os.environ["DYNAMIC_APP_URL"] = f"{proto}://{host}".rstrip("/")
    elif host and not os.environ.get("APP_URL"):
        os.environ["DYNAMIC_APP_URL"] = f"http://{host}".rstrip("/")
    return await call_next(request)

# Directories
OUTPUT_DIR = SKILL_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATIC_DIR = ROOT_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class GenerateRequest(BaseModel):
    prompt: str
    format: str = "all"  # 'composition', 'wav', or 'all'


class ConvertRequest(BaseModel):
    composition: Dict[str, Any]
    title: Optional[str] = "Converted Track"


@app.get("/api/health")
def health_check():
    return {"status": "ok", "time": datetime.datetime.now().isoformat()}


@app.get("/api/generations")
def get_generations():
    """Returns list of previous generations from Firestore / Private Cloud Storage."""
    history = get_all_generations()
    return {"status": "success", "generations": history}


@app.post("/api/generate")
def generate_endpoint(req: GenerateRequest):
    """
    Generate music from text prompt.
    Supports composition JSON format, WAV audio binary format, or all.
    Includes automated duration self-correction loop.
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    prompt = req.prompt.strip()
    fmt = req.format.lower().strip()

    try:
        res = generate_music(prompt, output_format=fmt)
        gen_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "id": gen_id,
            "prompt": prompt,
            "format": fmt,
            "created_at": timestamp,
            "composition": res.get("composition"),
            "midi_url": f"/output/{Path(res['midi_file']).name}" if "midi_file" in res else (
                f"/output/{Path(res['file_path']).name}" if res.get("format") == "midi" else None
            ),
            "wav_url": f"/output/{Path(res['wav_file']).name}" if "wav_file" in res else (
                f"/output/{Path(res['file_path']).name}" if res.get("format") == "wav" else None
            )
        }

        # Save durably to Firestore and upload to Private GCS
        saved_record = save_generation_record(record)
        return {"status": "success", "generation": saved_record}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/api/convert")
def convert_endpoint(req: ConvertRequest):
    """Convert composition JSON to MIDI and WAV audio with durable storage."""
    if not req.composition:
        raise HTTPException(status_code=400, detail="Composition data is required")

    try:
        comp_dict = req.composition
        midi_path = generate_midi_from_dict(comp_dict)

        sf_path = ensure_soundfont()
        options = ConvertOptions(soundfont_path=sf_path if os.path.exists(sf_path) else None)
        wav_path = convert_to_wav(midi_path, options=options)

        gen_id = str(uuid.uuid4())[:8]
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "id": gen_id,
            "prompt": f"Converted: {comp_dict.get('title', req.title)}",
            "format": "wav",
            "created_at": timestamp,
            "composition": comp_dict,
            "midi_url": f"/output/{Path(midi_path).name}",
            "wav_url": f"/output/{Path(wav_path).name}"
        }

        saved_record = save_generation_record(record)
        return {"status": "success", "generation": saved_record}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.api_route("/output/{filename}", methods=["GET", "HEAD"])
def serve_output_file(filename: str):
    """Serve output MIDI and WAV files securely from local cache or private GCS bucket."""
    file_path = OUTPUT_DIR / filename
    
    # If file not in local container cache, download securely from private GCS bucket
    if not file_path.exists():
        download_file_from_gcs(filename, str(file_path))

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "audio/wav" if filename.endswith(".wav") else "audio/midi"
    return FileResponse(file_path, media_type=media_type, filename=filename)


# Mount static assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
