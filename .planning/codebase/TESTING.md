# Testing Patterns

**Analysis Date:** 2026-01-30

## Test Framework

**Runner:**
- pytest 8.0.0+ (latest via `pyproject.toml`)
- Config location: `pyproject.toml` under `[tool.pytest.ini_options]`

**Assertion Library:**
- pytest assertions: `assert condition`, `assert array_equal()`, `pytest.raises()`
- NumPy assertions: `np.array_equal()` for comparing arrays

**Run Commands:**
```bash
pytest tests                           # Run all tests
pytest tests -v                        # Verbose output
pytest tests -k "test_name"            # Run specific test
pytest tests --cov=src                 # Run with coverage report
pytest tests --cov=src --cov-report=html    # Generate HTML coverage report
pytest tests -x                        # Stop on first failure
pytest tests --lf                      # Run last failed tests
```

**Configuration Details:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

## Test File Organization

**Location:**
- Co-located with source: Tests in `tests/` directory parallel to `src/`
- Test files mirror module structure:
  - `src/gridworld/environment.py` → `tests/test_gridworld.py` (combined GridWorld tests)
  - `src/main.py` → `tests/test_main.py`

**Naming:**
- Test files: `test_*.py` (e.g., `test_gridworld.py`, `test_main.py`)
- Test classes: `Test*` (e.g., `TestGridWorldConfig`, `TestGridWorldEnv`)
- Test functions: `test_*` (e.g., `test_default_config`, `test_reset`)

**Structure:**
```
tests/
├── __init__.py                  # Empty marker file
├── conftest.py                  # Shared fixtures
├── test_main.py                 # Tests for src/main.py
└── test_gridworld.py            # Tests for src/gridworld/
    ├── TestGridWorldConfig      # Config validation tests
    └── TestGridWorldEnv         # Environment behavior tests
```

## Test Structure

**Suite Organization:**
Test classes group related tests with shared setup:
```python
class TestGridWorldConfig:
    """Test GridWorldConfig validation."""

    def test_default_config(self):
        """Test that default configuration is valid."""
        config = GridWorldConfig()
        assert config.grid_size == 5

class TestGridWorldEnv:
    """Test GridWorld environment."""

    def test_initialization(self):
        """Test environment initializes correctly."""
        env = GridWorldEnv()
        assert env.action_space.n == 4
```

**Patterns:**
- **Setup pattern:** Each test creates its own fixtures inline
  ```python
  def test_reset(self):
      config = GridWorldConfig(start_pos=(1, 2))
      env = GridWorldEnv(config)
      obs, info = env.reset()
  ```
- **Teardown pattern:** No explicit teardown needed; objects garbage collected
- **Assertion pattern:** One logical assertion per test line (may have multiple assert statements)
  ```python
  obs, reward, terminated, truncated, info = env.step(GridWorldEnv.UP)
  assert np.array_equal(obs, np.array([1, 2]))
  assert reward == config.step_penalty
  assert not terminated
  ```

## Mocking

**Framework:** pytest's built-in `pytest.raises()` for exception testing (no mock library currently used)

**Patterns:**
- **Exception testing with context manager:**
  ```python
  def test_invalid_start_position(self):
      """Test that invalid start position raises error."""
      with pytest.raises(ValueError, match="Start position .* outside grid"):
          GridWorldConfig(grid_size=5, start_pos=(5, 5))
  ```

- **Match parameter for asserting error messages:**
  ```python
  with pytest.raises(ValueError, match="Start and goal positions cannot be the same"):
      GridWorldConfig(start_pos=(2, 2), goal_pos=(2, 2))
  ```

**What to Mock:**
- Nothing is currently mocked; tests use real environment instances
- Unit tests instantiate actual `GridWorldEnv` and `GridWorldConfig` objects
- Determinism achieved through seed control (`env.reset(seed=42)`)

**What NOT to Mock:**
- Environment internals: Tests verify actual behavior
- NumPy operations: Use actual numpy arrays
- Configuration validation: Test real validation logic

## Fixtures and Factories

**Test Data:**
No custom fixtures currently defined. Tests create inline fixtures:
```python
def test_reset(self):
    config = GridWorldConfig(start_pos=(1, 2))
    env = GridWorldEnv(config)
    obs, info = env.reset()
```

**Shared Fixture:**
- `conftest.py` contains example fixture (not actively used):
  ```python
  @pytest.fixture
  def sample_fixture():
      """Example fixture for testing."""
      return {"example": "data"}
  ```

**Location:**
- Shared fixtures defined in `tests/conftest.py`
- Test-specific fixtures created inline in test methods
- No factory functions; direct instantiation with parameters

## Coverage

**Requirements:**
- Target: 100% of `src/` code
- Coverage reports: Terminal (missing lines shown) and HTML
- Exclusions configured in `[tool.coverage.report]`:
  ```toml
  exclude_lines = [
      "pragma: no cover",
      "def __repr__",
      "raise AssertionError",
      "raise NotImplementedError",
      "if __name__ == .__main__.:",
      "if TYPE_CHECKING:",
  ]
  ```

**View Coverage:**
```bash
pytest tests --cov=src --cov-report=term-missing      # Terminal with missing lines
pytest tests --cov=src --cov-report=html              # HTML report in htmlcov/
open htmlcov/index.html                                # View HTML report
```

**Coverage Source:**
- Configuration: `pyproject.toml` under `[tool.coverage.run]` and `[tool.coverage.report]`
- Run automatically with `pytest` due to `addopts` in pytest config
- Missing lines highlighted in terminal output and HTML report

## Test Types

**Unit Tests:**
- **Scope:** Individual classes and functions
- **Approach:** Test one aspect per test method
- **Examples:**
  - `test_default_config()`: Validates default values
  - `test_step_up()`: Tests single action outcome
  - `test_invalid_action()`: Tests error handling
- **Location:** `tests/test_gridworld.py`, `tests/test_main.py`

**Integration Tests:**
- **Scope:** Environment behavior across multiple steps
- **Approach:** Verify state transitions and interactions
- **Examples:**
  - `test_multiple_episodes()`: Run multiple reset/step sequences
  - `test_reach_goal()`: Verify complete flow to goal
  - `test_max_steps_truncation()`: Check episode termination logic
- **Location:** Within same test classes as unit tests

**E2E Tests:**
- **Framework:** Not used
- **Status:** Manual play modes (`play.py`, `play_tkinter.py`) serve as manual E2E testing

## Common Patterns

**Async Testing:**
- Not applicable (no async/await code in codebase)

**Error Testing:**
Pattern for testing exceptions:
```python
def test_invalid_action(self):
    """Test that invalid action raises error."""
    env = GridWorldEnv()
    env.reset()

    with pytest.raises(ValueError, match="Invalid action"):
        env.step(5)
```

**Boundary Testing:**
Multiple tests verify edge cases:
```python
def test_boundary_top(self):
    """Test that agent cannot move beyond top boundary."""
    config = GridWorldConfig(start_pos=(2, 0), goal_pos=(4, 4))
    env = GridWorldEnv(config)
    env.reset()

    obs, _, _, _, _ = env.step(GridWorldEnv.UP)
    assert np.array_equal(obs, np.array([2, 0]))  # Stays at boundary

def test_boundary_bottom(self):
    """Test that agent cannot move beyond bottom boundary."""
    config = GridWorldConfig(start_pos=(2, 4), goal_pos=(0, 0))
    env = GridWorldEnv(config)
    env.reset()

    obs, _, _, _, _ = env.step(GridWorldEnv.DOWN)
    assert np.array_equal(obs, np.array([2, 4]))
```

**Parametrized Testing:**
Used in `test_main.py` for testing multiple inputs:
```python
@pytest.mark.parametrize(
    "name,expected",
    [
        ("Bob", "Hello, Bob!"),
        ("", "Hello, !"),
        ("123", "Hello, 123!"),
    ],
)
def test_hello_parametrized(name: str, expected: str):
    """Test hello with various inputs."""
    assert hello(name) == expected
```

**Reproducibility:**
Tests use seed control for deterministic behavior:
```python
def test_reproducibility_with_seed(self):
    """Test that setting seed makes environment deterministic."""
    env = GridWorldEnv()

    # Run episode with seed
    env.reset(seed=42)
    states1 = [tuple(env.agent_pos)]
    for _ in range(5):
        env.step(GridWorldEnv.RIGHT)
        states1.append(tuple(env.agent_pos))

    # Run again with same seed
    env.reset(seed=42)
    states2 = [tuple(env.agent_pos)]
    for _ in range(5):
        env.step(GridWorldEnv.RIGHT)
        states2.append(tuple(env.agent_pos))

    assert states1 == states2
```

---

*Testing analysis: 2026-01-30*
