# Codebase Structure

**Analysis Date:** 2026-01-30

## Directory Layout

```
reinforcement-learning-solitaire/
├── src/                       # Core package (installed via pyproject.toml)
│   ├── __init__.py
│   ├── main.py               # Template module (minimal)
│   ├── gridworld/            # Phase 1: GridWorld implementation
│   │   ├── __init__.py
│   │   ├── environment.py    # GridWorldEnv: Gymnasium-compatible environment
│   │   ├── agent.py          # Q-learning agent (stub, 1 line)
│   │   ├── config.py         # GridWorldConfig, QLearningConfig dataclasses
│   │   ├── play.py           # Terminal-based interactive game
│   │   ├── play_tkinter.py   # Tkinter GUI game + GridWorldTkinterRenderer
│   │   └── train.py          # Training demo (random agent for now)
│   ├── solitaire/            # Phase 2: Solitaire (scaffolding)
│   │   ├── __init__.py
│   │   └── agents/           # Agent implementations for solitaire
│   ├── visualization/        # Future: plots, animations
│   │   └── __init__.py
│   └── utils/                # Shared utilities
│       ├── __init__.py
│       └── metrics.py        # Performance tracking (stub, 1 line)
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_main.py         # Template tests
│   └── test_gridworld.py    # GridWorld environment tests (30+ tests)
├── experiments/              # Experiment results and logs
│   ├── gridworld/           # GridWorld experiments
│   └── solitaire/           # Solitaire experiments
├── docs/                     # Project documentation
│   ├── PROJECT_CONTEXT.md   # Project goals and current status
│   ├── FEATURES.md          # Feature roadmap
│   ├── ARCHITECTURE.md      # Technical decisions
│   ├── learning_notes/      # RL concepts and lessons
│   └── templates/           # FEATURE_TEMPLATE.md, REQUIREMENTS_TEMPLATE.md
├── scripts/                 # Standalone scripts
├── play_gridworld_tkinter.py # Entry point: GUI game
├── play_gridworld_terminal.py # Entry point: Terminal game
├── pyproject.toml           # Project config, dependencies, tool settings
├── README.md                # User-facing documentation
├── GETTING_STARTED.md       # Setup and quick start guide
└── .planning/               # GSD planning documents (created by map-codebase)
    └── codebase/           # Architecture and structure analysis
```

## Directory Purposes

**`src/`:**
- Purpose: Main Python package containing all source code
- Contains: Modules organized by functionality (gridworld, solitaire, visualization, utils)
- Key files: `environment.py`, `config.py`, `play_tkinter.py`

**`src/gridworld/`:**
- Purpose: Phase 1 implementation - GridWorld RL environment and interfaces
- Contains: Gymnasium environment, agents, config, multiple UIs (terminal + Tkinter)
- Key files:
  - `environment.py` - Core environment logic
  - `config.py` - Environment and agent configurations
  - `play_tkinter.py` - Tkinter-based interactive game
  - `train.py` - Training/demo script

**`src/solitaire/`:**
- Purpose: Phase 2 scaffold - Future Klondike Solitaire environment
- Contains: Game environment (future), agents directory for various implementations
- Key files: `agents/` subdirectory for Q-learning, DQN implementations

**`src/visualization/`:**
- Purpose: Future visualization utilities for learning metrics and policy visualization
- Contains: Heatmaps, learning curves, policy arrows, animations
- Status: Currently scaffolding; populated in Phase 1.3

**`src/utils/`:**
- Purpose: Shared utilities and helpers across all phases
- Contains: Metrics tracking, replay buffer (Phase 2), other cross-module code
- Key files: `metrics.py` for performance tracking

**`tests/`:**
- Purpose: Test suite for the entire project
- Contains: Unit tests organized by module
- Key files:
  - `test_gridworld.py` - 30+ tests for GridWorldEnv, GridWorldConfig validation
  - `conftest.py` - Shared pytest fixtures
  - `test_main.py` - Template tests

**`experiments/`:**
- Purpose: Store results and checkpoints from training runs
- Contains: Subdirectories for each phase (gridworld, solitaire)
- Status: Empty; populated during training

**`docs/`:**
- Purpose: Project documentation for humans and Claude
- Contains: Project context, features, architecture decisions, learning notes
- Key files:
  - `PROJECT_CONTEXT.md` - Goals, current status, roadmap
  - `FEATURES.md` - Feature list and roadmap
  - `ARCHITECTURE.md` - Technical decisions and rationale

**`scripts/`:**
- Purpose: Standalone utility scripts
- Status: Currently empty; for experiment runners, data processing, etc.

## Key File Locations

**Entry Points:**
- `play_gridworld_tkinter.py` - Main entry for GUI: `uv run play_gridworld_tkinter.py`
- `play_gridworld_terminal.py` - Main entry for terminal: `uv run play_gridworld_terminal.py`
- `src/gridworld/train.py` - Training demo: `uv run python -m src.gridworld.train`

**Configuration:**
- `pyproject.toml` - Dependencies, build config, tool settings (ruff, mypy, pytest)
- `src/gridworld/config.py` - Environment/agent hyperparameters (GridWorldConfig, QLearningConfig)

**Core Logic:**
- `src/gridworld/environment.py` - GridWorldEnv class, state management, step mechanics
- `src/gridworld/agent.py` - Q-learning agent (stub for Phase 1.2)

**Testing:**
- `tests/test_gridworld.py` - Comprehensive test suite for environment
- `tests/conftest.py` - Pytest configuration and fixtures
- `pyproject.toml` - `[tool.pytest.ini_options]` with coverage settings

## Naming Conventions

**Files:**
- Module files: `lowercase_with_underscores.py` (e.g., `play_gridworld_tkinter.py`)
- Entry points at root: `play_gridworld_*.py` pattern
- Test files: `test_<module>.py` (e.g., `test_gridworld.py`)

**Directories:**
- Package directories: `lowercase` (e.g., `src/gridworld/`)
- Phase-based grouping: `src/<phase_name>/` (e.g., `src/gridworld/`, `src/solitaire/`)
- Feature grouping: `src/<domain>/` (e.g., `src/visualization/`, `src/utils/`)

**Classes:**
- Main classes: `PascalCase` (e.g., `GridWorldEnv`, `GridWorldConfig`, `GridWorldTkinterRenderer`)
- Config classes: `<Feature>Config` (e.g., `GridWorldConfig`, `QLearningConfig`)

**Functions:**
- Functions and methods: `snake_case` (e.g., `get_action_from_key()`, `play_gridworld()`)
- Dunder methods: `__init__()`, `__post_init__()` (Python convention)

**Constants:**
- Class constants: `UPPERCASE` (e.g., `UP = 0`, `DOWN = 1` in GridWorldEnv)
- Color mappings: `COLORS = { "key": "#HEX" }` (e.g., in GridWorldTkinterRenderer)

## Where to Add New Code

**New Feature (e.g., Q-Learning Agent):**
- Primary code: `src/gridworld/agent.py` - Implement QLearningAgent class
- Tests: `tests/test_agents.py` - Create new test file for agent tests
- Integration: Update `src/gridworld/train.py` to use agent instead of random policy

**New Component/Module (e.g., Visualization):**
- Implementation: `src/visualization/plots.py` - Create new module
- Tests: `tests/test_visualization.py` - Test plotting functions
- Integration: Import and use in `train.py` or play interfaces

**New Game Interface (e.g., Web UI):**
- Implementation: `src/gridworld/play_web.py` - New interface module
- Entry point: `play_gridworld_web.py` at root level
- Config: Reference existing GridWorldConfig, inherit pattern from `play_tkinter.py`

**Utilities and Helpers:**
- Shared helpers: `src/utils/<domain>.py` - New utility module
- Metrics: `src/utils/metrics.py` - Add tracking functions
- Replay buffer: `src/utils/replay_buffer.py` - Add in Phase 2

**Configuration:**
- New environment settings: Add to `GridWorldConfig.__post_init__()` validation
- New agent hyperparameters: Add QLearningConfig field, add validator
- Tool config: Edit `pyproject.toml` `[tool.ruff]`, `[tool.mypy]`, etc.

## Special Directories

**`.planning/codebase/`:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (created by `/gsd:map-codebase`)
- Committed: Yes (version control for architecture decisions)
- Contains: ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md

**`htmlcov/`:**
- Purpose: Coverage report output from pytest
- Generated: Yes (by `pytest --cov-report=html`)
- Committed: No (add to `.gitignore`)

**`experiments/`:**
- Purpose: Training results, model checkpoints, experiment logs
- Generated: Yes (created by training scripts)
- Committed: Selectively (include summaries, exclude large model files)

**`docs/`:**
- Purpose: Version-controlled documentation for developers
- Generated: Manually by developers
- Committed: Yes (architecture decisions, feature progress)

---

*Structure analysis: 2026-01-30*
