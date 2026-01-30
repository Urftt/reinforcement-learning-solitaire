# Codebase Concerns

**Analysis Date:** 2026-01-30

## Tech Debt

**Empty/Stub Modules:**
- Issue: Several modules created in project structure but not implemented
- Files: `src/gridworld/agent.py`, `src/solitaire/__init__.py`, `src/visualization/__init__.py`, `src/utils/metrics.py`
- Impact: Blocks planned Q-learning training features (Feature 1.2). Visualization roadmap cannot proceed. Metrics tracking unavailable for learning analysis.
- Fix approach: Implement these modules sequentially as per roadmap. Q-learning agent is critical blocker for Phase 1 completion.

**Unused Dependency:**
- Issue: `pygame-ce>=2.4.0` listed in dependencies but not imported or used anywhere
- Files: `pyproject.toml` (line 15)
- Impact: Adds unnecessary build overhead. Initial project only uses Tkinter (built-in) for graphics. Wastes time installing unused library.
- Fix approach: Remove pygame-ce from main dependencies. Add to optional `visualization` group only when implementing pygame-based visualizations later (if needed).

**Main Module Out of Scope:**
- Issue: `src/main.py` contains placeholder "Hello, World!" code unrelated to RL project
- Files: `src/main.py`, `tests/test_main.py`
- Impact: Creates confusion about actual project entry points. Tests in `test_main.py` don't contribute to project goals.
- Fix approach: Either replace with actual RL training entry point or remove. Consider moving placeholder tests to a separate template location.

## Architectural Gaps

**Missing Q-Learning Agent Module:**
- Problem: `src/gridworld/agent.py` exists but is empty. README roadmap requires this for Feature 1.2
- Files: `src/gridworld/agent.py`
- Blocks: Training loop implementation, learning experiments, all Q-learning features
- Priority: **CRITICAL** - Blocks entire learning phase of project
- Current state: Repository in Feature 1.1 (environment complete). Agent is next major feature.

**No Training Pipeline:**
- Problem: `src/gridworld/train.py` currently contains only a demo with random agent. No actual Q-learning training loop.
- Files: `src/gridworld/train.py` (82 lines, mostly demo code)
- Blocks: Cannot run any actual RL experiments or learning. Cannot collect metrics or visualizations.
- Fix approach: Implement `train()` function that accepts agent type, runs episodes, tracks metrics, saves results

**Visualization Framework Not Started:**
- Problem: `src/visualization/` exists but is empty. No heatmaps, policy visualizations, or learning curves implemented
- Files: `src/visualization/__init__.py` (empty)
- Blocks: Feature 1.3 (visualization). Cannot see what agent is learning. Delays experimentation understanding.
- Priority: HIGH - Needed for Phase 1 completion but comes after agent implementation

**Metrics Tracking Missing:**
- Problem: `src/utils/metrics.py` is empty. No centralized metrics collection during training
- Files: `src/utils/metrics.py`
- Impact: Must implement ad-hoc logging in training code. Harder to analyze learning curves or compare experiments.
- Fix approach: Create MetricsTracker class to collect episode rewards, steps, exploration rates, convergence measures

## Fragile Areas

**Terminal Game Hard to Exit Cleanly:**
- Files: `src/gridworld/play.py`
- Why fragile: EOFError/KeyboardInterrupt catching at line 133 only catches in input loop. If user interrupts during rendering, may leave terminal in bad state.
- Safe modification: Wrap entire play_gridworld() body in try-finally to ensure cleanup
- Test coverage: `test_gridworld.py` doesn't test user interrupt scenarios

**Tkinter Event Loop Coupling:**
- Files: `src/gridworld/play_tkinter.py`
- Why fragile: Complex Tkinter event loop at lines 386-495. Uses `root.after()` callbacks with mutable state (`game_over` list at line 384). State modification through side effects is error-prone.
- Safe modification: Extract game logic from Tkinter layer - separate game state machine from UI rendering
- Current risk: Small timing errors in callback scheduling could cause missed inputs or duplicate actions

**Grid Position Coordinate Convention Not Enforced:**
- Files: `src/gridworld/environment.py`, `src/gridworld/config.py`
- Why fragile: Code uses (x, y) tuples throughout but rendering code at lines 154-158 of `environment.py` uses `grid[y, x]` indexing. This works but relies on developer remembering the convention. Easy to swap coordinates.
- Safe modification: Create Position/Coordinate class or type alias to make convention explicit. Use consistent unpacking: `x, y = pos` everywhere
- Test coverage: Position conversion tested in `test_gridworld.py` lines 208-223 but not all rendering paths covered

**Reward Structure Deeply Embedded:**
- Files: `src/gridworld/config.py`, `src/gridworld/environment.py`
- Why fragile: Rewards hardcoded in GridWorldConfig. Changing reward values requires modifying config instances. No centralized reward function.
- Safe modification: Create RewardFunction abstraction to make reward structures pluggable and testable
- Risk: If Solitaire phase reuses GridWorld code, reward structure conflicts could arise

**Trail Management in Tkinter Renderer:**
- Files: `src/gridworld/play_tkinter.py` (lines 49-51, 223-229)
- Why fragile: Trail stored as list that grows unbounded (limited only by max_trail_length=50). If rendering is slow, trail could overflow memory. Line 226 checks `if not self.trail or self.trail[-1] != pos_tuple` which could miss duplicates on edge cases.
- Safe modification: Use deque with maxlen instead of list. This enforces size limit automatically.

## Known Bugs & Issues

**Potential State Index Boundary Bug:**
- Symptoms: If grid_size changes after state index created, mapping will be incorrect
- Files: `src/gridworld/environment.py` (lines 194-205)
- Trigger: Create environment with grid_size=5, get state indices, then create new environment with grid_size=7 and try to use old indices
- Current status: Not a practical bug since each environment maintains own grid_size, but could confuse users mixing environments
- Workaround: Always use fresh state indices from the same environment instance

**Obstacle on Start Position Not Validated:**
- Symptoms: Can create config where start position is also an obstacle (both allowed independently)
- Files: `src/gridworld/config.py` (lines 30-51)
- Trigger: `GridWorldConfig(start_pos=(2,2), obstacles=[(2,2)])`
- Current state: No validation prevents this. Environment would immediately hit obstacle penalty on first frame after reset.
- Priority: LOW - Unlikely in normal use, but `__post_init__` validation should catch this
- Fix approach: Add check in config validation that start/goal/obstacles don't overlap

## Performance Considerations

**Grid Rendering Not Optimized:**
- Problem: Every render call deletes entire canvas and redraws all elements
- Files: `src/gridworld/play_tkinter.py` (line 124: `self.canvas.delete("all")`)
- Current capacity: Works fine for 7x7 grids (Feature 1.1), but not scalable to larger grids
- When it breaks: 50x50+ grid rendering would lag. Solitaire environment (Phase 2) might need faster rendering.
- Scaling path: Implement dirty rectangle optimization or layer-based rendering. Only redraw changed elements.

**Trail Storage Unbounded:**
- Problem: Trail array grows during game, reaches 50 elements, then removes from front
- Files: `src/gridworld/play_tkinter.py` (lines 228-229)
- Current capacity: Trail limited to 50 positions, acceptable for single games
- Limit: If multiple episodes run long (1000+ steps), garbage collection overhead could accumulate
- Scaling path: Use fixed-size deque. Memory usage then O(1) instead of O(n)

## Test Coverage Gaps

**Terminal Play Mode Not Tested:**
- What's not tested: `src/gridworld/play.py` interactive gameplay logic
- Files: `src/gridworld/play.py` (entire file)
- Risk: Difficulty selection, input parsing, episode restart logic untested. Could have hidden bugs in user flow.
- Priority: MEDIUM - This is user-facing, should have integration tests

**Tkinter GUI Not Tested:**
- What's not tested: `src/gridworld/play_tkinter.py` rendering and event handling
- Files: `src/gridworld/play_tkinter.py` (entire file)
- Risk: GUI bugs discovered only at runtime. Keyboard handling, window close events, game loop scheduling not validated.
- Priority: MEDIUM - Complex code path, needs unit tests for event handling at minimum

**Configuration Validation Incomplete:**
- What's not tested: Obstacle-on-start/goal overlap validation (currently no validation exists)
- Files: `src/gridworld/config.py`
- Risk: Invalid configurations could silently fail during training
- Priority: LOW - Validation not yet implemented

**Edge Case: Empty Obstacle List:**
- What's not tested: Grid with no obstacles (only goal)
- Files: `src/gridworld/environment.py`, `tests/test_gridworld.py`
- Current state: `test_gridworld.py` line 49 tests with default config but no explicit test for obstacles=[]
- Risk: LOW - This works (easy difficulty uses this), but not explicitly validated

## Security Considerations

**User Input Not Validated in Terminal Game:**
- Risk: If input is from untrusted source, long strings could cause issues
- Files: `src/gridworld/play.py` (line 132: `input()`)
- Current mitigation: Interactive prompt only accepts single characters (validated at line 155)
- Recommendations: Already handled safely by length checking. No security concern for interactive mode.

**Command-Line Arguments Not Sanitized:**
- Risk: If project expands to file paths or model loading, --difficulty args should be enumerated (they are)
- Files: `play_gridworld_tkinter.py`, `play_gridworld_terminal.py`
- Current mitigation: argparse restricts to choices=["easy", "medium", "hard"]
- Recommendations: Continue using argparse choices for all CLI inputs

## Missing Critical Features

**Q-Learning Training Not Implemented:**
- Problem: No way to actually train an agent
- Blocks: Entire Phase 1 learning component. Cannot run Feature 1.2 experiments.
- Priority: **CRITICAL** for project roadmap

**Experimentation Framework Missing:**
- Problem: No way to save/load trained agents or run hyperparameter sweeps
- Blocks: Cannot systematically test learning rate, discount factor effects
- Priority: HIGH - Needed for Phase 1 experimentation goals

**Visualization System Not Built:**
- Problem: No learning curves, Q-value heatmaps, or policy visualizations
- Blocks: Cannot understand what agent learned (Feature 1.3)
- Priority: HIGH - Crucial for learning insights

**Solitaire Environment Not Started:**
- Problem: Phase 2 skeleton only (`src/solitaire/__init__.py`)
- Blocks: All Phase 2 work
- Priority: MEDIUM - Planned for later phase, not blocking Phase 1

## Scaling Limits

**Q-Table Memory for Large Grids:**
- Current capacity: 5x5=25 states, 7x7=49 states work fine
- Limit: 100x100 grid = 10,000 states, still manageable. 1000x1000 = 1M states, Q-table = ~8MB with float64
- Scaling path: For very large grids (10000x10000), need function approximation (DQN). This is planned for Solitaire phase.

**Tkinter Rendering Resolution:**
- Current capacity: 7x7 grid with 80px cells = 560x560px window fits on all displays
- Limit: 20x20 grid at 80px = 1600x1600px exceeds typical monitor. Text becomes unreadable.
- Scaling path: Reduce cell_size or implement zoom/pan for large grids

## Dependency Concerns

**Gymnasium Dependency Choice:**
- Status: Stable choice, used for environment interface
- Risk: LOW - Gymnasium is maintained successor to gym
- Current state: Correctly specified as `gymnasium>=0.29.0`

**No Pinned Versions:**
- Risk: Future dependency releases could break code
- Current state: Using `>=` constraints only (pyproject.toml lines 11-15)
- Impact: Different environments may have different resolved versions
- Recommendation: Consider generating lock file or adding upper bounds for critical libraries once code is more stable

**PyGame Unnecessarily Installed:**
- Risk: Won't be used until visualization phase, adds build time now
- Current state: Listed in main dependencies
- Recommendation: Move to optional `visualization` dependencies group (already has deep-rl group at line 26)

---

*Concerns audit: 2026-01-30*
