# Features

> **Purpose**: Track feature status and roadmap so Claude Code knows what's next.
> **Update frequency**: Update whenever feature status changes or new features are planned.

## Feature Status

### ✅ Completed

#### Project Setup
- **Completed**: 2026-01-25
- **Description**: Repository structure, dependencies, documentation templates
- **Location**: Root directory
- **Notes**: Using uv for package management, PEP8 code style

#### 1.1 GridWorld Environment
- **Completed**: 2026-01-25
- **Description**: Gymnasium-compatible GridWorld environment with configurable size, obstacles, goals
- **Location**: [src/gridworld/environment.py](../src/gridworld/environment.py), [src/gridworld/config.py](../src/gridworld/config.py)
- **Tests**: [tests/test_gridworld.py](../tests/test_gridworld.py) - 25 tests, 99% coverage
- **Notes**:
  - Implements full Gymnasium interface (reset, step, render)
  - Configurable 5x5 grid (default) with customizable size
  - Single goal, configurable obstacles
  - Reward structure: goal=+10, obstacle=-10, step=-1 (all configurable)
  - State: agent (x, y) position
  - Actions: up (0), down (1), left (2), right (3)
  - Helper methods for state indexing (useful for Q-table)
  - Boundary checking prevents agent from moving off grid
  - Max steps per episode to prevent infinite loops

#### 1.2 Q-Learning Agent
- **Completed**: 2026-01-26
- **Description**: Tabular Q-learning implementation from scratch with epsilon-greedy exploration
- **Location**: [src/gridworld/agent.py](../src/gridworld/agent.py), [src/gridworld/config.py](../src/gridworld/config.py)
- **Tests**: [tests/test_agent.py](../tests/test_agent.py) - 18 tests, 100% coverage
- **Notes**:
  - Q-table as NumPy array [num_states, num_actions]
  - Epsilon-greedy exploration with exponential decay
  - Bellman equation implementation for Q-value updates: Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]
  - Configurable hyperparameters: learning_rate (α=0.1), discount_factor (γ=0.99), epsilon (start=1.0, end=0.01, decay=0.995)
  - Methods: select_action(), learn(), decay_epsilon()
  - Helper methods: get_q_values(), get_policy(), get_state_value()
  - Persistence: save/load Q-table with pickle
  - Integration tested with GridWorld environment

---

### 🚧 In Progress

_No features currently in progress_

---

### 📋 Planned - Phase 1: GridWorld

#### 1.3 Training Loop & Metrics
- **Priority**: High
- **Description**: Training infrastructure with comprehensive metrics tracking
- **Depends on**: 1.2 Q-Learning Agent
- **Estimated effort**: Small
- **Notes**:
  - Episode loop with convergence checking
  - Track: rewards per episode, steps per episode, epsilon decay
  - Save Q-table for later analysis
  - Config management for hyperparameters

#### 1.4 Visualization Suite
- **Priority**: High
- **Description**: Rich visualizations to understand learning
- **Depends on**: 1.2 Q-Learning Agent, 1.3 Training Loop
- **Estimated effort**: Medium
- **Notes**:
  - Q-value heatmaps (one per action or max over actions)
  - Policy arrows showing learned behavior
  - Learning curves: reward, steps, exploration rate
  - Animated training progress (optional but cool!)
  - Grid visualization showing agent, obstacles, goals

#### 1.5 Experimentation Framework
- **Priority**: Medium
- **Description**: Easy hyperparameter sweeps and comparison
- **Depends on**: 1.3 Training Loop, 1.4 Visualization Suite
- **Estimated effort**: Small
- **Notes**:
  - Run multiple seeds for statistical significance
  - Compare learning rates, discount factors, exploration strategies
  - Generate comparison plots
  - Save experiment results in structured format

#### 1.6 Advanced GridWorld Features
- **Priority**: Low
- **Description**: Extensions to make GridWorld more interesting
- **Depends on**: 1.1-1.4 completed
- **Estimated effort**: Small-Medium
- **Notes**:
  - Multiple goals with different rewards
  - Stochastic transitions (slip probability)
  - Partial observability
  - Dynamic obstacles

---

### 📋 Planned - Phase 2: Solitaire

#### 2.1 Solitaire Game Logic
- **Priority**: Medium (after Phase 1)
- **Description**: Full Klondike Solitaire implementation
- **Depends on**: Phase 1 completed
- **Estimated effort**: Large
- **Notes**:
  - Card representation
  - Pile management (tableau, foundation, stock, waste)
  - Legal move generation
  - Win condition checking
  - Start with simplified rules, add complexity iteratively

#### 2.2 Solitaire Environment
- **Priority**: Medium
- **Description**: Gymnasium-compatible Solitaire environment
- **Depends on**: 2.1 Solitaire Game Logic
- **Estimated effort**: Medium
- **Notes**:
  - State representation (high-dimensional!)
  - Action space (multiple move types)
  - Reward shaping (critical for learning)
  - Episode termination (win, loss, stuck)

#### 2.3 Feature Engineering for Tabular Methods
- **Priority**: Medium
- **Description**: State abstraction to make tabular methods feasible
- **Depends on**: 2.2 Solitaire Environment
- **Estimated effort**: Medium
- **Notes**:
  - Hand-crafted features
  - State clustering/binning
  - Evaluate: can tabular methods work at all?

#### 2.4 Deep Q-Network (DQN)
- **Priority**: High (Phase 2 main goal)
- **Description**: DQN implementation with experience replay and target network
- **Depends on**: 2.2 Solitaire Environment
- **Estimated effort**: Large
- **Notes**:
  - Neural network architecture
  - Experience replay buffer
  - Target network
  - Comparison with stable-baselines3 implementation

#### 2.5 Advanced DQN Techniques
- **Priority**: Low
- **Description**: Double DQN, prioritized replay, dueling DQN
- **Depends on**: 2.4 DQN working
- **Estimated effort**: Medium-Large
- **Notes**: Incremental improvements to baseline DQN

---

### 🤔 Ideas / Backlog

- **Other RL algorithms**: SARSA, Expected SARSA, Monte Carlo methods
- **Policy gradient methods**: REINFORCE, A2C, PPO (out of initial scope)
- **Other card games**: Blackjack, Spider Solitaire
- **Interactive play**: Human vs agent, or human-assisted training
- **Web visualization**: Interactive dashboard for training progress
- **Transfer learning**: Train on one solitaire variant, transfer to another

---

### ❌ Rejected / Won't Implement

_Nothing rejected yet_

---

## Feature Dependencies

```
Phase 1: GridWorld
├─ 1.1 GridWorld Environment
├─ 1.2 Q-Learning Agent (requires 1.1)
├─ 1.3 Training Loop (requires 1.2)
├─ 1.4 Visualization Suite (requires 1.2, 1.3)
├─ 1.5 Experimentation Framework (requires 1.3, 1.4)
└─ 1.6 Advanced GridWorld (requires 1.1-1.4)

Phase 2: Solitaire (requires Phase 1)
├─ 2.1 Solitaire Game Logic
├─ 2.2 Solitaire Environment (requires 2.1)
├─ 2.3 Feature Engineering (requires 2.2)
├─ 2.4 Deep Q-Network (requires 2.2)
└─ 2.5 Advanced DQN (requires 2.4)
```

## Next Steps

**Immediate priorities**:
1. [x] 1.1: Implement GridWorld environment
2. [x] 1.2: Implement Q-learning agent
3. [ ] 1.3: Build training loop with metrics
4. [ ] 1.4: Create visualization suite

**Waiting on**:
- None - ready for Phase 1 training loop!
