# Getting Started with RL Learning Project

Welcome! This guide will help you get started with your reinforcement learning journey.

## Project Setup

### 1. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync

# Install pre-commit hooks (ensures code quality)
uv run pre-commit install
```

### 2. Verify Installation

```bash
# Run tests (should pass with minimal template tests)
uv run pytest

# Check code quality
uv run ruff check .
uv run ruff format .
```

## Phase 1: GridWorld - Your First RL Environment

### What You'll Build

1. **GridWorld Environment**: A simple grid where an agent learns to navigate to a goal
2. **Q-Learning Agent**: Implement the classic tabular RL algorithm from scratch
3. **Visualizations**: See your agent learn in real-time through plots and heatmaps
4. **Experiments**: Test different hyperparameters and understand their effects

### Recommended Learning Path

#### Step 1: Understand the Environment (2-3 hours)
- **Goal**: Build a simple 5x5 GridWorld with Gymnasium interface
- **Files**: [src/gridworld/environment.py](src/gridworld/environment.py)
- **Key concepts**: State space, action space, rewards, transitions
- **Success criteria**: Agent can take actions and receive rewards

**Start here**:
```bash
# Ask Claude Code to help you implement the GridWorld environment
# "Let's implement the GridWorld environment together. Start with a 5x5 grid."
```

#### Step 2: Implement Q-Learning (3-4 hours)
- **Goal**: Build Q-learning agent from scratch
- **Files**: [src/gridworld/agent.py](src/gridworld/agent.py), [src/gridworld/config.py](src/gridworld/config.py)
- **Key concepts**: Q-table, Bellman equation, epsilon-greedy exploration
- **Success criteria**: Agent improves over time

**What you'll learn**:
- How Q-values represent expected future rewards
- Why exploration matters (epsilon-greedy)
- How the Bellman equation updates Q-values
- The role of learning rate and discount factor

#### Step 3: Training Loop & Metrics (1-2 hours)
- **Goal**: Create training infrastructure
- **Files**: [src/gridworld/train.py](src/gridworld/train.py), [src/utils/metrics.py](src/utils/metrics.py)
- **Key concepts**: Episode structure, convergence, metrics tracking
- **Success criteria**: Track learning progress over episodes

#### Step 4: Visualize Learning (2-3 hours)
- **Goal**: See what your agent is learning
- **Files**: [src/visualization/plots.py](src/visualization/plots.py)
- **Visualizations to create**:
  - Q-value heatmaps (one per action direction)
  - Policy visualization (arrows showing learned behavior)
  - Learning curves (reward per episode, steps per episode)
  - Exploration rate decay

**This is where it gets exciting!** Watching Q-values evolve and seeing the agent's policy emerge is incredibly satisfying.

#### Step 5: Experiment! (Ongoing)
- **Goal**: Understand hyperparameter effects
- **Key experiments**:
  - Learning rate: Try 0.01, 0.1, 0.5
  - Discount factor: Try 0.9, 0.95, 0.99
  - Exploration: Compare epsilon-greedy strategies
  - Environment complexity: Add obstacles, multiple goals

## Key RL Concepts You'll Master

### Q-Learning Fundamentals
- **Q-value**: Expected future reward for taking action `a` in state `s`
- **Bellman Update**: `Q(s,a) ← Q(s,a) + α[r + γ·max Q(s',a') - Q(s,a)]`
- **Policy**: Extract best action from Q-values: `π(s) = argmax_a Q(s,a)`

### The Learning Process
1. **Initialize**: Random Q-values (or zeros)
2. **Explore**: Take actions (sometimes random, sometimes greedy)
3. **Observe**: Get reward and new state
4. **Update**: Adjust Q-values using Bellman equation
5. **Repeat**: Until convergence or max episodes

### Common Pitfalls to Watch For
- **Too little exploration**: Agent gets stuck in local optima
- **Too much exploration**: Agent never exploits what it learned
- **Learning rate too high**: Q-values oscillate, never converge
- **Learning rate too low**: Learning is painfully slow
- **Wrong reward structure**: Agent learns the wrong behavior

## Tips for Success

### 1. Start Small
- Begin with a tiny 3x3 grid
- Add complexity gradually
- Make sure each piece works before adding more

### 2. Visualize Everything
- Don't just look at final results
- Watch learning happen episode by episode
- Animated visualizations help debug

### 3. Document Your Learning
- Keep notes in [docs/learning_notes/](docs/learning_notes/)
- Explain concepts in your own words
- Document "aha!" moments and problems you solved

### 4. Test Your Understanding
- Can you predict what will happen when you change a hyperparameter?
- Can you explain why the agent learned a particular policy?
- Can you identify why learning isn't converging?

## Next Steps After GridWorld

Once you've mastered GridWorld, you'll be ready for Phase 2: Solitaire!

You'll apply the same principles but face new challenges:
- **Large state space**: Can't store all Q-values in a table
- **Complex actions**: Multiple types of moves
- **Sparse rewards**: Win/loss at the end, not every step
- **Function approximation**: Neural networks (DQN) instead of tables

But don't worry about that yet. Focus on GridWorld and build a solid foundation.

## Resources

### Within This Project
- [README.md](README.md) - Project overview
- [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) - Project goals and status
- [docs/FEATURES.md](docs/FEATURES.md) - Feature roadmap
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical decisions

### External Resources (for deeper understanding)
- Sutton & Barto "Reinforcement Learning: An Introduction" (the RL bible)
- David Silver's RL course (YouTube)
- Gymnasium documentation (environment interface)

## Getting Help

Working with Claude Code:
```
# When starting a new session, always begin with:
"Read the project docs to understand where we are, then let's continue with [task]"

# For learning-focused development:
"Explain the concept of [X] as we implement it"
"Why did we make this design decision?"
"What would happen if we changed [Y]?"

# For debugging:
"The agent isn't learning. Let's visualize Q-values to see what's happening"
"Help me understand why this reward structure isn't working"
```

## Let's Begin!

Ready to start? Here's your first task:

```bash
# Start with the environment
"Let's implement the GridWorld environment following the Gymnasium interface.
Start with a simple 5x5 grid with one goal and one obstacle."
```

Have fun, and remember: the goal is understanding, not speed. Take time to visualize, experiment, and really grasp what's happening.

**You're about to learn by building. Let's go!**
