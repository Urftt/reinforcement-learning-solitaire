# Coding Conventions

**Analysis Date:** 2026-01-30

## Naming Patterns

**Files:**
- Snake case for all module files: `environment.py`, `config.py`, `play_tkinter.py`
- Entry point file: `main.py`
- Module directories use snake case: `gridworld/`, `utils/`, `visualization/`, `solitaire/`

**Functions:**
- Snake case for function names: `get_action_from_key()`, `print_instructions()`, `demo_random_agent()`
- Private functions use leading underscore: `_on_key_press()`, `_on_close()`
- Action verbs in function names: `get_`, `print_`, `play_`, `demo_`

**Variables:**
- Snake case for all variables: `step_count`, `total_reward`, `agent_pos`, `grid_size`
- Constants in UPPERCASE: `UP = 0`, `DOWN = 1`, `LEFT = 2`, `RIGHT = 3`
- Class constants in UPPERCASE: `COLORS = {...}`, `metadata = {...}`
- Private attributes use leading underscore: `_obstacles_set`, `_on_key_press()`

**Types:**
- Use standard Python type hints throughout
- Union types with pipe operator: `int | None`, `str | None` (Python 3.10+)
- Type hints on function parameters and return values
- Type hints on class attributes using annotations

## Code Style

**Formatting:**
- Ruff formatter with double quotes: `"string"` (not `'string'`)
- Line length: 100 characters (configured in `pyproject.toml`)
- Indentation: 4 spaces
- Blank lines: 2 between top-level definitions, 1 between methods

**Linting:**
- Tool: Ruff (version 0.1.0+)
- Config location: `pyproject.toml` under `[tool.ruff]`
- Active rules: E, W, F, I, B, C4, UP
  - E: pycodestyle errors
  - W: pycodestyle warnings
  - F: pyflakes
  - I: isort (import sorting)
  - B: flake8-bugbear
  - C4: flake8-comprehensions
  - UP: pyupgrade
- Pre-commit hooks: Ruff runs both linting (`--fix`) and formatting automatically

**Type Checking:**
- Tool: mypy (version 1.8.0+)
- Config location: `pyproject.toml` under `[tool.mypy]`
- Settings:
  - Python version: 3.10+
  - `warn_return_any: true`
  - `check_untyped_defs: true`
  - `no_implicit_optional: true`
  - Full type checking disabled (`disallow_untyped_defs: false`, `disallow_incomplete_defs: false`)

## Import Organization

**Order:**
1. Standard library imports: `import sys`, `from typing import ...`, `from dataclasses import dataclass`
2. Third-party imports: `import numpy as np`, `import gymnasium as gym`, `import tkinter as tk`
3. Local imports: `from src.gridworld.config import ...`, `from src.gridworld.environment import ...`

**Path Aliases:**
- All imports use absolute paths from project root: `from src.gridworld.config import GridWorldConfig`
- No relative imports (e.g., avoid `from .config import GridWorldConfig`)
- Local module imports use `src.` prefix consistently

**Import Sorting:**
- Ruff's isort (`I` rule) enforces import order
- Imports are automatically sorted by pre-commit hooks

## Error Handling

**Patterns:**
- Raise specific exceptions with descriptive messages: `ValueError`, `RuntimeError`
- Include context in error messages: `raise ValueError(f"Start position {self.start_pos} outside grid")`
- Validate inputs in `__post_init__` for dataclasses
- Validation in constructors ensures invalid states cannot be created

**Specific Patterns:**
- Configuration validation in `GridWorldConfig.__post_init__()`:
  ```python
  if not (0 <= self.start_pos[0] < self.grid_size and 0 <= self.start_pos[1] < self.grid_size):
      raise ValueError(f"Start position {self.start_pos} outside grid")
  ```
- Initialization checks in environment methods:
  ```python
  if self.agent_pos is None:
      raise RuntimeError("Environment not initialized. Call reset() first.")
  ```
- Action validation in step method:
  ```python
  else:
      raise ValueError(f"Invalid action: {action}. Must be 0-3.")
  ```

**Exception Types Used:**
- `ValueError`: For invalid configuration or parameters
- `RuntimeError`: For invalid state transitions or operation sequencing
- `KeyboardInterrupt`: Caught for graceful shutdown in interactive sessions

## Logging

**Framework:** `print()` for user output (no formal logging framework currently used)

**Patterns:**
- Use `print()` with f-strings for formatted output
- Separate output with visual separators using `"=" * 50`
- Include newlines for readability: `print("\n" + "=" * 60)`
- Statistics printing follows consistent format with aligned columns
- Messages use emoji for visual distinction in interactive sessions: `"🎯 Reached goal!"`, `"💥 Hit obstacle!"`

**Print Examples:**
```python
print(f"Episode {episode + 1}")
print(f"Reward: {reward:.1f}")
print(f"  Total reward: {total_reward:.1f}")
```

## Comments

**When to Comment:**
- Comments explain WHY, not WHAT. Code is self-documenting; comments explain intent.
- Comments appear above the code they describe
- Inline comments rare; use descriptive variable/function names instead
- Comments in docstrings preferred over inline comments

**JSDoc/DocStrings:**
- All modules start with docstring explaining purpose
- All classes have docstrings with description and attributes listed
- All functions have docstrings with Args, Returns, and optional description
- Docstring format: Google-style with triple quotes
- Module docstrings use triple quotes on single line for brief modules:
  ```python
  """Main module for the project."""
  ```
- Multi-line docstrings format:
  ```python
  """Brief description.

  Longer description if needed.
  """
  ```

**Docstring Examples:**
- Class docstring with attributes:
  ```python
  """A simple GridWorld environment for reinforcement learning.

  The agent starts at a position and must navigate to a goal while avoiding
  obstacles. Each step incurs a small penalty, obstacles give a large penalty,
  and reaching the goal gives a large reward.

  State space: Discrete (x, y) position on the grid
  Action space: Discrete with 4 actions (up, down, left, right)
  """
  ```
- Function docstring:
  ```python
  """Convert keyboard input to action.

  Args:
      key: User input key

  Returns:
      Action integer or None if invalid
  """
  ```

## Function Design

**Size:**
- Functions are focused and concise
- Average function length: 10-50 lines for methods, 5-30 for utilities
- Longer functions (70+ lines) exist for specific purposes (e.g., `render()` method with many drawing operations)

**Parameters:**
- Use specific parameters over generic kwargs
- Type hints required for all parameters
- Optional parameters use defaults: `seed: int | None = None`, `options: dict[str, Any] | None = None`
- Maximum 5-6 parameters typical; larger configs use config objects

**Return Values:**
- Multiple return values as tuples for Gymnasium-compatible methods:
  ```python
  def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
  ```
- Single return value if simple
- Dictionary returns for structured data: `info: dict[str, Any]`

## Module Design

**Exports:**
- Modules expose primary classes and functions at module level
- Example: `src/gridworld/config.py` exports `GridWorldConfig`, `QLearningConfig`
- No `__all__` restrictions; public API determined by naming (no leading underscore)

**Barrel Files:**
- Module `__init__.py` files currently minimal (empty or single comment)
- No aggregation of exports (no `from .config import *`)
- Modules imported directly: `from src.gridworld.config import GridWorldConfig`

**Module Organization:**
- One primary class per module when possible: `config.py` has configs, `environment.py` has `GridWorldEnv`
- Related classes grouped: `config.py` contains both `GridWorldConfig` and `QLearningConfig`
- Utility functions in dedicated `utils/` directory

---

*Convention analysis: 2026-01-30*
