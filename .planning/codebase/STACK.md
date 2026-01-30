# Technology Stack

**Analysis Date:** 2026-01-30

## Languages

**Primary:**
- Python 3.10+ - All application code, entry points, and utilities
  - Minimum version: 3.10 (specified in `pyproject.toml`)
  - Tested against: 3.10, 3.11, 3.12 (in CI matrix)

**Secondary:**
- YAML - Configuration and CI/CD workflows
- TOML - Project configuration and tool settings

## Runtime

**Environment:**
- CPython 3.10, 3.11, 3.12
- Target Python versions verified via GitHub Actions CI

**Package Manager:**
- uv 0.x (latest) - Fast, modern Python package manager
- Lockfile: `uv.lock` (present, checked into repository)
- Installation: `uv sync` / `uv sync --all-extras`

## Frameworks

**Core RL Frameworks:**
- `gymnasium>=0.29.0` - Standardized RL environment interface (successor to OpenAI Gym)
  - Used by `src/gridworld/environment.py` for GridWorldEnv implementation
  - Provides `gym.Env`, `spaces.Discrete`, `spaces.Box`

**Numerical & Scientific:**
- `numpy>=1.24.0` - Array operations, matrix math for RL algorithms
  - Used throughout: GridWorld state representation, Q-learning tables, agent updates

**Visualization:**
- `matplotlib>=3.7.0` - Plotting learning curves, heatmaps of Q-values, policy visualization
  - Used by: `src/visualization/` (plots.py, animations.py - TBD)

**GUI Framework:**
- Built-in `tkinter` (no dependency, part of Python stdlib)
  - Entry point: `play_gridworld_tkinter.py`
  - Tkinter renderer: `src/gridworld/play_tkinter.py`
  - Reason: "GUARANTEED TO WORK ON MACOS" per code comments; no external GUI deps needed

**Graphics/Games:**
- `pygame-ce>=2.4.0` (Community Edition) - For Phase 2 Solitaire visualization
  - Not yet actively used in Phase 1
  - Chosen for better wheel support vs. official pygame

**Progress & Output:**
- `tqdm>=4.65.0` - Progress bars for training loops and experiments

**Testing:**
- `pytest>=8.0.0` - Test runner
  - Config: `pyproject.toml` [tool.pytest.ini_options]
  - Test discovery: `tests/test_*.py`, `Test*` classes, `test_*` functions
  - Coverage: `pytest-cov>=4.1.0` integrated with `--cov=src`

**Code Quality:**
- `ruff>=0.1.0` - Linting + formatting (combined tool)
  - Linting checks: E, W, F, I, B, C4, UP (see pyproject.toml)
  - Line length: 100 characters
  - Format: double quotes, 4-space indent
- `mypy>=1.8.0` - Static type checking
  - Python version target: 3.10
  - Config: `pyproject.toml` [tool.mypy]
  - Enabled checks: `warn_return_any`, `check_untyped_defs`, `no_implicit_optional`

**Pre-commit:**
- `pre-commit>=3.6.0` - Git hook framework for automated checks
  - Config: `.pre-commit-config.yaml`
  - Hooks: ruff (lint + format), mypy, standard checks (trailing whitespace, merge conflicts, etc.)
  - Custom hook: `scripts/check_docs_update.py` (documentation sync check)

**Optional Dependencies (Phase 2):**
- `torch>=2.0.0` (deep-rl extra) - For DQN implementation (Phase 2, install when needed)

## Key Dependencies

**Critical (Runtime - Phase 1):**
- `gymnasium` 1.2.3 - Core RL environment interface; gridworld depends on this
- `numpy` 2.2.6 (Python <3.11) / 2.4.1 (Python >=3.11) - Mathematical operations, state representation
- `matplotlib` 3.10.8 - Learning visualization
- `tqdm` 4.68.1 - Progress tracking
- `pygame-ce` 2.4.1+ - Game rendering (Phase 2)

**Build & Development:**
- `hatchling` - Build backend for wheel generation
- `cloudpickle` - Object serialization (used by gymnasium for environment pickling)
- `farama-notifications` - Notification system (gymnasium dependency)

**Infrastructure (CI/CD):**
- `codecov` - Coverage reporting to Codecov service
- GitHub Actions - CI/CD runner (free for public repos)
  - Workflow: `.github/workflows/ci.yml`
  - Jobs: Code quality checks, test matrix (Python 3.10-3.12)

## Configuration

**Environment:**
- Local `.env` file support: Not enforced, but .gitignore includes `.env*`
- Development: No external API secrets required for Phase 1 (pure ML)
- Python path: Entry points use `sys.path.insert(0, project_root)` for relative imports

**Build:**
- Config files:
  - `pyproject.toml` - Unified project config (project metadata, dependencies, tool configs)
  - `uv.lock` - Dependency lockfile (commit to repo for reproducibility)
  - `.pre-commit-config.yaml` - Git hooks
  - `.github/workflows/ci.yml` - GitHub Actions workflow

**Tool Configurations (all in pyproject.toml):**
- **[tool.ruff]**: line-length=100, target-version="py310"
- **[tool.ruff.lint]**: E, W, F, I, B, C4, UP (no ignored rules)
- **[tool.ruff.format]**: double-quotes, 4-space indent
- **[tool.mypy]**: Strict checks on untyped code, no implicit optionals
- **[tool.pytest.ini_options]**: Coverage enabled, verbose output, HTML report generation
- **[tool.coverage.run]**: Source tracking for `src/`, omit tests
- **[tool.coverage.report]**: Exclude `__repr__`, `NotImplementedError`, `if __name__ == "__main__"`

## Platform Requirements

**Development:**
- macOS, Linux, or Windows with Python 3.10+
- Tkinter (usually pre-installed with Python)
- Git for version control
- uv package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

**Production (Phase 1):**
- Python 3.10+ runtime
- ~500MB disk for dependencies (including dev tools)
- No GPU required (Q-learning is CPU-bound)

**Production (Phase 2 with DQN):**
- GPU recommended (CUDA/ROCm compatible if using torch on GPU)
- Additional ~2GB for torch library

## Dependency Management

**Install all dependencies:**
```bash
uv sync                   # Install prod + dev
uv sync --all-extras      # Include optional groups (deep-rl)
```

**Add new dependency:**
```bash
uv add package_name       # Adds to [project] dependencies
uv add -d package_name    # Adds to [project.optional-dependencies.dev]
```

**Lock updates:**
```bash
uv lock                   # Regenerate lock file after changes
uv sync                   # Apply locked versions locally
```

---

*Stack analysis: 2026-01-30*
