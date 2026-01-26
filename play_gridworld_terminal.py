"""Entry point for terminal GridWorld game - run this file directly from VSCode!

Usage: Click the Run button (▶️) in VSCode or press F5
"""

import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.gridworld.play import main  # noqa: E402

if __name__ == "__main__":
    main()
