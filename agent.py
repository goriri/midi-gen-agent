"""
Root agent.py exporting root_agent for ADK Agent Hub and agents-cli standards.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from midi_agent.agent import root_agent

__all__ = ["root_agent"]
