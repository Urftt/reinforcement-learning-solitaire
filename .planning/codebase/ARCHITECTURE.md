# Architecture

**Analysis Date:** 2026-01-30

## Pattern Overview

**Overall:** Layered Gymnasium-based RL Framework with Progressive Complexity

**Key Characteristics:**
- Modular separation of environment, agents, and interfaces
- Gymnasium standard compliance for extensibility
- Two-phase progression: GridWorld (Phase 1) → Solitaire (Phase 2)
- Configuration-driven environment design
- Multiple interaction modes: Terminal, Tkinter GUI, training
- Support for tabular methods (Q-learning) with future deep RL (DQN)

## Layers

**Environment Layer:**
- Purpose: Provides Gymnasium-compliant RL environments
- Location: `src/gridworld/environment.py`, `src/solitaire/`
- Contains: GridWorldEnv class with observation/action spaces, step mechanics, reward logic
- Depends on: Gymnasium, NumPy, config modules
- Used by: Training agents, UI renderers, player interfaces

**Configuration Layer:**
- Purpose: Centralize hyperparameters and environment settings
- Location: `src/gridworld/config.py`
- Contains: GridWorldConfig (environment settings), QLearningConfig (agent hyperparameters)
- Depends on: Python dataclasses
- Used by: Environment initialization, agent training

**Agent Layer:**
- Purpose: Implement RL learning algorithms
- Location: `src/gridworld/agent.py`, `src/solitaire/agents/`
- Contains: Q-learning agent (stub), future DQN implementations
- Depends on: Environment, config, NumPy
- Used by: Training loop

**Interface Layer:**
- Purpose: Present playable and trainable environments to users
- Location: `src/gridworld/play.py`, `src/gridworld/play_tkinter.py`, `src/gridworld/train.py`
- Contains: Terminal UI, Tkinter renderer, training demos
- Depends on: Environment, config, Tkinter
- Used by: Entry points (`play_gridworld_tkinter.py`, `play_gridworld_terminal.py`)

**Utilities Layer:**
- Purpose: Cross-cutting concerns and reusable components
- Location: `src/utils/`
- Contains: Metrics tracking, visualization helpers, replay buffers (future)
- Depends on: NumPy, Matplotlib
- Used by: Agents, training loops, visualization

## Data Flow

**Interactive Play Flow:**

1. User launches entry point (`play_gridworld_tkinter.py`)
2. Entry point imports interface module (`src/gridworld/play_tkinter.py`)
3. Interface creates GridWorldConfig with difficulty preset
4. Config validates and initializes environment parameters
5. GridWorldEnv instance created with config
6. GridWorldTkinterRenderer created with environment reference
7. Game loop processes keyboard input → environment steps → renderer updates
8. Environment returns (observation, reward, terminated, truncated, info)
9. Renderer displays state; loop repeats until game-over or quit

**Training Flow:**

1. `src/gridworld/train.py` creates config and environment
2. For each episode:
   - Reset environment to initial state
   - While not done:
     - Agent selects action (random for demo, Q-learning future)
     - Environment executes step
     - Reward logged and accumulated
   - Episode summary printed

**State Management:**
- Environment maintains internal state: `agent_pos` (np.ndarray), `step_count` (int)
- Config remains immutable after creation
- Renderer maintains trail history for visualization
- Episode stats tracked locally in play loops

## Key Abstractions

**GridWorldEnv:**
- Purpose: Represents the RL environment following Gymnasium protocol
- Examples: `src/gridworld/environment.py`
- Pattern: Inherits from `gym.Env`, implements `reset()`, `step()`, `render()`
- Converts 2D (x, y) positions to 1D state indices for Q-table compatibility
- Enforces boundary constraints and collision detection

**GridWorldConfig:**
- Purpose: Immutable configuration object for environment parameters
- Examples: `src/gridworld/config.py` (GridWorldConfig dataclass)
- Pattern: Python dataclass with `__post_init__` validation
- Presets available: Easy (5x5 no obstacles), Medium (5x5 2 obstacles), Hard (7x7 6 obstacles)

**GridWorldTkinterRenderer:**
- Purpose: Bridge between environment state and Tkinter graphics
- Examples: `src/gridworld/play_tkinter.py`
- Pattern: Maintains renderer state (trail, colors) while exposing game loop integration
- Methods: `render()` for display, `get_action()` for input polling, event handlers
- Non-blocking design uses `after()` scheduling for responsive event loop

**QLearningConfig:**
- Purpose: Holds hyperparameters for Q-learning agent
- Examples: `src/gridworld/config.py` (QLearningConfig dataclass)
- Pattern: Dataclass with learning rate, discount factor, epsilon-decay settings

## Entry Points

**GUI Play (Tkinter):**
- Location: `play_gridworld_tkinter.py` (root level)
- Triggers: `uv run play_gridworld_tkinter.py [--difficulty {easy|medium|hard}]`
- Responsibilities: Path setup, argument parsing, calls `src/gridworld/play_tkinter.main()`
- Works reliably on macOS with native Tkinter

**Terminal Play:**
- Location: `play_gridworld_terminal.py` (root level)
- Triggers: `uv run play_gridworld_terminal.py [--difficulty {easy|medium|hard}]`
- Responsibilities: WASD/arrow input, text rendering, game loop
- Fallback when GUI unavailable

**Training Demo:**
- Location: `src/gridworld/train.py`
- Triggers: `uv run python -m src.gridworld.train`
- Responsibilities: Random policy demo, logs episode results
- Future: Will implement Q-learning training

## Error Handling

**Strategy:** Fail-fast with descriptive error messages; validation at config layer

**Patterns:**
- GridWorldConfig validates all positions during `__post_init__` before env creation
- GridWorldEnv raises `RuntimeError` if step() called before reset()
- GridWorldEnv raises `ValueError` for invalid actions (only 0-3 accepted)
- Boundary checks in step() prevent invalid moves (clamp to grid limits)
- Try-except in entry points for KeyboardInterrupt graceful shutdown

## Cross-Cutting Concerns

**Logging:** Console print statements for demo/training; future: Python logging module

**Validation:** GridWorldConfig dataclass validates bounds and state machine constraints

**Authentication:** Not applicable (single-user offline game)

**State Initialization:** Environment.reset() idempotent; can reset multiple times

---

*Architecture analysis: 2026-01-30*
