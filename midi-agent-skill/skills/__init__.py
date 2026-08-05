"""Skills module for MIDI generation."""

from .generate_midi import generate_midi, generate_midi_from_dict
from .normalize_composition import normalize_composition, normalize_to_dict
from .refine_composition import refine_composition, refine_from_dict, extend_composition
from .convert_to_wav import convert_to_wav, get_conversion_status, ConvertOptions

__all__ = [
    "generate_midi",
    "generate_midi_from_dict",
    "normalize_composition",
    "normalize_to_dict",
    "refine_composition",
    "refine_from_dict",
    "extend_composition",
    "convert_to_wav",
    "get_conversion_status",
    "ConvertOptions"
]
