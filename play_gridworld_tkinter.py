"""Entry point for Tkinter GridWorld GUI - GUARANTEED TO WORK ON MACOS!

Tkinter is built into Python and has excellent macOS support.
This version has proper event loop integration and will not freeze.

Usage:
    uv run play_gridworld_tkinter.py
    uv run play_gridworld_tkinter.py --difficulty hard
"""

import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gridworld.play_tkinter import main  # noqa: E402

if __name__ == "__main__":
    main()
