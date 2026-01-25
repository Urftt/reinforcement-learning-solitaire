# Architecture

> **Purpose**: Document technical decisions and design so Claude Code understands the codebase structure.
> **Update frequency**: Update when making significant architectural decisions or changes.

## Project Structure

```
.
├── src/
│   ├── gridworld/           # Phase 1: GridWorld environment and agent
│   │   ├── environment.py   # GridWorld Gymnasium environment
│   │   ├── agent.py         # Q-learning agent
│   │   ├── train.py         # Training loops and experiments
│   │   └── config.py        # Hyperparameters
│   ├── solitaire/           # Phase 2: Solitaire game and agents
│   │   ├── environment.py   # Solitaire Gymnasium environment
│   │   ├── game.py          # Game logic
│   │   └── agents/          # DQN and other agents
│   ├── visualization/       # Plotting and animation utilities
│   │   ├── plots.py         # Static plots (learning curves, heatmaps)
│   │   └── animations.py    # Animated visualizations
│   └── utils/               # Shared utilities
│       └── metrics.py       # Metrics tracking
├── experiments/             # Saved experiment results
├── tests/                   # Test suite
└── docs/                    # Documentation
    └── learning_notes/      # RL concept notes and lessons learned
```

## Key Architectural Decisions

### Use Gymnasium/OpenAI Gym Interface
**Date**: 2026-01-25

**Context**: Need a standard interface for RL environments that's compatible with existing tools.

**Decision**: All environments will follow the Gymnasium (formerly OpenAI Gym) API interface.

**Rationale**:
- Standard interface used across RL community
- Makes environments compatible with existing RL libraries
- Clean separation between environment and agent
- Easy to test environments independently

**Alternatives considered**:
- Custom interface: More flexibility but less compatibility
- Stable-baselines3 wrapper: Too heavyweight for learning project

**Consequences**:
- All environments must implement: `reset()`, `step()`, `render()`, observation/action spaces
- Easy to swap environments or use existing tools
- Can compare with standard benchmarks

---

### Build Algorithms From Scratch First
**Date**: 2026-01-25

**Context**: This is a learning project focused on understanding RL deeply.

**Decision**: Implement core RL algorithms (Q-learning, DQN) from scratch before using libraries.

**Rationale**:
- Deep understanding comes from implementation
- Debug and visualize every component
- Understand design choices and tradeoffs
- Libraries are black boxes until you've built it yourself

**Alternatives considered**:
- Use stable-baselines3 from start: Faster but less learning
- Mix of custom and library code: Confusion about which is which

**Consequences**:
- More code to write and maintain
- Better understanding of algorithms
- Can use libraries later for comparison/validation
- Visualization is built-in from the start

---

### Separate Concerns: Environment, Agent, Training, Visualization
**Date**: 2026-01-25

**Context**: RL projects can become messy without clear separation.

**Decision**: Strict separation between environment logic, agent logic, training loops, and visualization.

**Rationale**:
- Environment shouldn't know about agents
- Agents shouldn't know about training schedules
- Visualization is for analysis, not core functionality
- Each component testable in isolation

**Consequences**:
- More files but clearer organization
- Easy to swap agents or environments
- Training scripts orchestrate components
- Visualization can be added/removed without affecting core logic

---

### Configuration Over Hard-Coding
**Date**: 2026-01-25

**Context**: RL requires extensive hyperparameter tuning.

**Decision**: Use config files/dataclasses for all hyperparameters and experiment settings.

**Rationale**:
- Easy to run experiments with different settings
- Reproducible experiments
- Clear documentation of what was tested
- No magic numbers in code

**Consequences**:
- Config files for each environment/agent
- Experiment results include config used
- Slightly more boilerplate but much clearer

---

## Design Patterns

**Patterns used in this project**:

- **Strategy Pattern**: Different RL agents (Q-learning, DQN, etc.) implement the same interface, can be swapped easily
- **Template Method**: Training loops follow a common pattern (reset → step → learn → log → repeat)
- **Observer Pattern**: Metrics collection observes training without interfering
- **Factory Pattern** (future): For creating different agent/environment configurations

## Code Organization

**Module structure**:
- **Environments**: Self-contained, implement Gymnasium interface
- **Agents**: Contain learning algorithm, policy selection, and parameter updates
- **Training**: Orchestrate episodes, handle metrics, save results
- **Visualization**: Pure functions that take data and produce plots
- **Utils**: Shared functionality (metrics, replay buffers)

**Naming conventions**:
- Classes: `CamelCase` (e.g., `GridWorldEnv`, `QLearningAgent`)
- Functions: `snake_case` (e.g., `train_agent`, `plot_learning_curve`)
- Constants: `UPPER_CASE` (e.g., `MAX_EPISODES`, `DEFAULT_LEARNING_RATE`)
- Private methods: `_leading_underscore`

**File organization rules**:
- One environment per file
- One agent type per file
- Separate config from implementation
- Tests mirror source structure

## External Dependencies

**Key libraries**:

| Library | Purpose | Why chosen |
|---------|---------|------------|
| `numpy` | Array operations, Q-tables | Standard for numerical computing |
| `gymnasium` | Environment interfaces | Standard RL environment API |
| `matplotlib` | Visualization | Rich plotting capabilities, animations |
| `torch` | Deep RL (Phase 2) | Most popular deep learning library for RL |
| `tqdm` | Progress bars | User-friendly training progress |

**Development dependencies**:
| Library | Purpose | Why chosen |
|---------|---------|------------|
| `pytest` | Testing | Standard Python testing framework |
| `ruff` | Linting/formatting | Fast, modern, all-in-one tool |
| `mypy` | Type checking | Catch bugs early, better IDE support |

## Data Flow

**Training Loop**:
```
Config → Environment.reset() → Initial State
                ↓
    ┌───────────────────────────┐
    │  Episode Loop:            │
    │  State → Agent.select_action() → Action  │
    │  Action → Environment.step() → (Next State, Reward, Done) │
    │  Transition → Agent.learn() → Update Q-values │
    │  Metrics → Logger → Visualization │
    └───────────────────────────┘
                ↓
     Results (Q-table, metrics, plots)
```

**Visualization Pipeline**:
```
Training Metrics → Aggregation → Plot Functions → Saved Figures
Q-values → Heatmap Generation → Animated GIF/Video
Policy → Arrow Overlay → Grid Visualization
```

## Testing Strategy

**Test organization**:
- Unit tests for individual components
- Integration tests for environment-agent interaction
- Regression tests for algorithm correctness

**What to test**:
- Environment state transitions are correct
- Rewards are calculated properly
- Agent's Q-value updates follow Bellman equation
- Policy extraction is correct
- Edge cases (terminal states, invalid actions)

**What not to test**:
- Exact learning curves (stochastic)
- Convergence speed (varies)
- Visualization appearance (manual inspection)

**RL-specific testing**:
- Deterministic environments for reproducibility
- Small state spaces for exhaustive testing
- Known-optimal solutions for validation

## Performance Considerations

**Current phase (GridWorld)**:
- Performance is not a concern
- Prioritize clarity and correctness
- NumPy arrays are sufficient

**Future phase (Solitaire)**:
- State representation may need optimization
- Neural network training will be bottleneck
- Consider GPU acceleration for DQN
- Experience replay buffer needs efficient sampling

**Optimization philosophy**:
- Measure first, optimize later
- Don't prematurely optimize
- Focus on algorithmic correctness before speed

## Future Architecture Plans

**Planned additions**:
- Replay buffer for DQN (Phase 2)
- Neural network abstractions for function approximation
- Experiment tracking (weights & biases integration?)
- Parallel environment execution for faster training

**Scalability considerations**:
- Current architecture scales well from GridWorld to Solitaire
- May need distributed training for complex environments
- Visualization might need optimization for large experiments

## Notes for Claude Code

**Code style preferences**:
- PEP8 strict compliance
- Type hints for function signatures
- Docstrings for all public functions (explain RL concepts)
- Clear variable names that reflect RL terminology (e.g., `q_values`, not `vals`)

**RL-specific coding guidelines**:
- Always include comments explaining Bellman updates
- Document reward structures clearly
- Explain exploration strategies in detail
- Include assertions for shape checking (easy to mess up dimensions)

**When to ask before changing**:
- Changing environment reward structure
- Modifying core RL algorithm implementations
- Adding new dependencies
- Refactoring that changes experiment results

**Preferred abstractions**:
- Keep RL algorithms explicit (not hidden in base classes)
- Simple inheritance over complex hierarchies
- Composition over inheritance for agent capabilities
