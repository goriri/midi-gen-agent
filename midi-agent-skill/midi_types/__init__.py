"""Types module for MIDI generation."""

from .music import Note, Track, Composition
from .gm_instruments import (
    GM_INSTRUMENTS,
    INSTRUMENT_ALIASES,
    resolve_instrument,
    get_instrument_name,
    get_instruments_by_category
)

__all__ = [
    "Note",
    "Track",
    "Composition",
    "GM_INSTRUMENTS",
    "INSTRUMENT_ALIASES",
    "resolve_instrument",
    "get_instrument_name",
    "get_instruments_by_category"
]
