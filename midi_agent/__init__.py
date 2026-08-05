"""
MIDI Agent package.
"""

from midi_agent.agent import root_agent
from midi_agent.tools import generate_music, generate_composition_text, generate_midi_binary, generate_wav_binary

__all__ = [
    "root_agent",
    "generate_music",
    "generate_composition_text",
    "generate_midi_binary",
    "generate_wav_binary",
]
