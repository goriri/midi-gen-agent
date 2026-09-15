# ADK MIDI Agent & Composition Studio 🎵

An enterprise-grade, agentic AI music composition studio built with **Google ADK (Agent Development Kit)**, **Google GenAI**, **FastAPI**, **FluidSynth**, and **Google Cloud Platform**.

The agent parses natural language text prompts (in Chinese or English) specifying musical attributes such as BPM, key/scale, General MIDI instruments, drum constraints, and target duration. It generates structured music scores in composition JSON format, synthesizes binary MIDI files, and renders full WAV audio.

---

## Key Features

- **Prompt Spec Parsing & Music Theory Alignment**:
  Automatically extracts BPM, Key (e.g., C Major, A Minor), General MIDI instrument mapping, 4/4 time signature, and drum constraints.
- **Bar-Precise Measure Targeting & Duration Self-Correction**:
  Calculates measure boundaries to match target durations (e.g. 60s at 72 BPM) and runs an automated self-correction loop to guarantee duration within $\pm 5$ seconds.
- **Multi-Format Generation**:
  - **Composition Score (JSON)**: Full note-level score suitable for musical staff rendering.
  - **MIDI File (`.mid`)**: General MIDI binary file via `midiutil`.
  - **WAV Audio (`.wav`)**: High-quality audio synthesis via `FluidSynth` and GM SoundFont.
- **Modern Responsive Web UI**:
  - Sample prompt chips for quick testing.
  - Output format toggle (`Composition`, `WAV`, `Both`).
  - Interactive composition viewer and embedded HTML5 audio player.
  - 1-click JSON score to WAV audio converter.
  - Public generation history gallery.
- **Durable Enterprise Storage**:
  - **Google Cloud Firestore**: Persists generation metadata JSON.
  - **Private Google Cloud Storage (GCS)**: Stores WAV and MIDI binary files securely.
  - **Secure Server Proxying**: Backend server proxies private GCS audio streaming without exposing public bucket access.

---

## Project Structure

```
midi-gen/
├── midi_agent/                 # ADK MIDI Agent Core
│   ├── agent.py                # Google ADK Root Agent
│   ├── gm_mapping.py           # Chinese/English Instrument & Spec Parser
│   ├── music_generator.py      # Music Theory Engine & Duration Self-Correction
│   ├── tools.py                # ADK Tools for Composition, MIDI & WAV
│   └── db.py                   # Firestore & Private GCS Storage Manager
├── midi-agent-skill/           # Integrated MIDI & FluidSynth Conversion Skill
├── static/                     # Web UI Frontend (HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/                      # Comprehensive Unit & Integration Test Suite
│   ├── test_midi_agent.py
│   ├── test_web_server.py
│   └── test_duration_conformance.py
├── server.py                   # FastAPI Server & REST API Endpoints
├── Dockerfile                  # Multi-stage Debian Docker Build for Cloud Run
├── requirements.txt            # Python Dependencies
├── .env.example                # Public Environment Variables Template
└── README.md
```

---

## Quickstart & Local Setup

### Prerequisites

- Python 3.11+
- System packages for FluidSynth audio synthesis:
  ```bash
  sudo apt-get update && sudo apt-get install -y fluidsynth fluid-soundfont-gm
  ```

### Installation

1. **Clone the Repository**:
   ```bash
   git clone git@github.com:goriri/midi-gen-agent.git
   cd midi-gen-agent
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your GCP project details:
   ```bash
   cp .env.example .env
   ```
   *Note: Sensitive configuration values in `.env` are excluded from Git.*

3. **Set Up Virtual Environment & Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Run Web Studio Locally**:
   ```bash
   python server.py
   ```
   Open your browser at `http://localhost:8000`.

---

## Running Tests

Execute the full automated test suite (unit tests, API end-to-end checks, and duration self-correction verification):

```bash
python -m unittest discover -s tests
```

---

## One-Click Deployment (AgentHub & Standalone)

To deploy the entire agent stack (Cloud Run container, Firestore, GCS bucket, IAM bindings, and optional Gemini Enterprise registration) in one click:

```bash
# Standalone deployment
./deploy.sh <YOUR_GCP_PROJECT_ID>

# One-click deployment with Gemini Enterprise registration
./deploy.sh <YOUR_GCP_PROJECT_ID> --ge <YOUR_GE_APP_ID>
```

### Agent-to-Agent (A2A) & Gemini Enterprise Endpoints

The service natively serves the Google Agent-to-Agent (A2A) protocol:
- **A2A Agent Card**: `https://<SERVICE_URL>/a2a/app/.well-known/agent-card.json`
- **A2A JSON-RPC**: `https://<SERVICE_URL>/a2a/app`
- **Interactive Web Studio**: `https://<SERVICE_URL>/`

---

## License

MIT License.
