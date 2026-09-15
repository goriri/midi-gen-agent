"""
ADK Agent definition for MIDI Music Generator.
Handles text-to-MIDI composition, binary MIDI creation, and WAV conversion using midi-agent-skill.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from google.adk.agents import Agent
from midi_agent.tools import (
    generate_music,
    generate_composition_text,
    generate_midi_binary,
    generate_wav_binary,
)

SYSTEM_INSTRUCTION = """
You are an expert AI Music Composer agent powered by Google ADK and General MIDI (GM) music theory standards.
Your goal is to generate MIDI music based on user prompts in both English and Chinese.

Capabilities:
1. **Composition Format (Text / JSON)**: Generate a structured musical composition dictionary containing title, BPM, tracks, General MIDI instruments, and note sequences (pitch and duration notation).
2. **Binary MIDI (.mid)**: Generate and render a standard General MIDI file.
3. **Binary Audio WAV (.wav)**: Convert generated MIDI into high-quality WAV audio binary files.

Instructions & Best Practices:
- Parse all explicit user constraints carefully:
  - **BPM**: e.g., 72BPM, 120BPM
  - **Key & Scale**: e.g., C大调 (C Major), A小调 (A Minor)
  - **Instruments**: Map Chinese & English names to GM instruments (e.g. 原声钢琴 -> acoustic-grand-piano, 尼龙木吉他 -> acoustic-guitar-nylon, 小提琴 -> violin, 风铃 -> tinkle-bell)
  - **Drums**: Respect "不要鼓点" / "no drums" constraints
  - **Output Format**: Determine whether the user asked for composition format (text/JSON), MIDI binary, or WAV audio binary format.
- Always invoke the appropriate tool (`generate_music`, `generate_composition_text`, `generate_midi_binary`, or `generate_wav_binary`).
- Provide a summary of the generated music (BPM, Key, Instruments, Duration, Output file path) in your final response.
"""

import os

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

root_agent = Agent(
    name="midi_agent",
    model=MODEL,
    instruction=SYSTEM_INSTRUCTION,
    description="Generates MIDI music in composition format (text/JSON) or binary files (.mid / .wav) from text prompts.",
    tools=[generate_music, generate_composition_text, generate_midi_binary, generate_wav_binary]
)
