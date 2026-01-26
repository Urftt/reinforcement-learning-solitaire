# Reinforcement Learning: From GridWorld to Solitaire

A hands-on learning project to deeply understand reinforcement learning by implementing algorithms from scratch, progressing from simple grid-based environments to training agents that play Klondike Solitaire.

## 🎯 Project Goals

**Learning RL fundamentals through implementation:**

- Build RL algorithms from scratch to understand them deeply
- Progress from tabular methods (Q-learning) to deep RL (DQN)
- Create rich visualizations to see what agents are learning
- Establish clean, reusable code patterns for RL development

**Two-phase approach:**
1. **Phase 1 - GridWorld**: Master fundamentals with a simple environment
2. **Phase 2 - Solitaire**: Apply knowledge to a challenging card game

## ✨ Features

### Phase 1: GridWorld Fundamentals
- **GridWorld Environment**: Custom Gymnasium-compatible environment
- **Q-Learning Agent**: Tabular Q-learning from scratch
- **Rich Visualizations**:
  - Heatmaps of Q-values evolving over time
  - Policy visualization (arrows showing agent's learned behavior)
  - Learning curves (rewards, steps, exploration rate)
- **Experimentation Framework**: Easy to test different hyperparameters

### Phase 2: Klondike Solitaire (Coming Soon)
- **Solitaire Environment**: Full Klondike rules with Gymnasium interface
- **Tabular Methods**: State abstraction for tractable state space
- **Deep Q-Network (DQN)**: Handle large state spaces with neural networks
- **Performance Metrics**: Win rates, game length, learning efficiency

### Development Tools
- **📦 uv**: Ultra-fast Python package management
- **🔍 Code Quality**: Ruff (linting + formatting) + mypy (type checking)
- **🧪 Testing**: pytest with coverage reporting
- **📊 Visualization**: Matplotlib for RL metrics and learning progress

## 🚀 Quick Start

### 1. Set Up the Environment

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify everything works
uv run pytest
uv run ruff check .
```

### 2. Run Phase 1 - GridWorld

```bash
# Play GridWorld with GUI (Tkinter - works great on macOS!)
uv run play_gridworld_tkinter.py                    # Medium difficulty (default)
uv run play_gridworld_tkinter.py --difficulty easy  # 5x5, no obstacles
uv run play_gridworld_tkinter.py --difficulty hard  # 7x7, 6 obstacles

# Or play in terminal (text-based, works anywhere)
uv run play_gridworld_terminal.py
uv run play_gridworld_terminal.py --difficulty easy

# Watch a random agent (see baseline performance)
uv run python -m src.gridworld.train

# Train a Q-learning agent (coming soon in Feature 1.2)
# uv run python -m src.gridworld.train --agent qlearning

# Visualize the learned policy (coming soon in Feature 1.4)
# uv run python -m src.gridworld.visualize
```

### 3. Explore the Code

Start with these files:
- [play_gridworld_tkinter.py](play_gridworld_tkinter.py) - Entry point for GUI game (Tkinter)
- [src/gridworld/play_tkinter.py](src/gridworld/play_tkinter.py) - Tkinter renderer and game loop
- [src/gridworld/play.py](src/gridworld/play.py) - Terminal-based gameplay
- [src/gridworld/environment.py](src/gridworld/environment.py) - GridWorld environment (Gymnasium-compatible)
- [src/gridworld/config.py](src/gridworld/config.py) - Configuration for environment and agents
- [src/gridworld/train.py](src/gridworld/train.py) - Training demo (random agent for now)
- [src/gridworld/agent.py](src/gridworld/agent.py) - Q-learning agent (coming in Feature 1.2)

## 📖 Learning Roadmap

### Phase 1: GridWorld Fundamentals
**Goal**: Master tabular RL and build visualization toolkit

1. **Environment Setup**
   - Implement GridWorld with configurable size, obstacles, rewards
   - Follow Gymnasium interface for compatibility

2. **Q-Learning Implementation**
   - Build Q-table from scratch
   - Implement epsilon-greedy exploration
   - Understand Bellman updates through visualization

3. **Visualization & Analysis**
   - Heatmaps of Q-values
   - Policy arrows
   - Learning curves (reward per episode, steps to goal)
   - Exploration rate decay

4. **Experimentation**
   - Test different learning rates, discount factors
   - Compare exploration strategies
   - Understand convergence behavior

### Phase 2: Klondike Solitaire
**Goal**: Apply RL to a real-world challenge

1. **Game Environment**
   - Implement Klondike rules
   - Define state representation
   - Design reward structure

2. **Tabular Approach**
   - State abstraction techniques
   - Feature engineering for tractability

3. **Deep Q-Network (DQN)**
   - Neural network function approximation
   - Experience replay
   - Target network

4. **Advanced Techniques**
   - Double DQN
   - Prioritized experience replay
   - Compare with baseline strategies

## 📁 Project Structure

```
.
├── src/
│   ├── gridworld/            # Phase 1: GridWorld implementation
│   │   ├── environment.py    # GridWorld environment (Gymnasium-compatible)
│   │   ├── agent.py          # Q-learning agent
│   │   ├── train.py          # Training loop and experiments
│   │   └── config.py         # Hyperparameters and configuration
│   ├── solitaire/            # Phase 2: Solitaire (future)
│   │   ├── environment.py    # Solitaire environment
│   │   ├── game.py           # Game logic
│   │   └── agents/           # Various agent implementations
│   ├── visualization/        # Visualization utilities
│   │   ├── plots.py          # Training curves, heatmaps
│   │   └── animations.py     # Animated visualizations
│   └── utils/                # Shared utilities
│       ├── metrics.py        # Performance tracking
│       └── replay_buffer.py  # For DQN (Phase 2)
├── tests/                    # Test suite
│   ├── test_gridworld.py
│   └── test_agents.py
├── docs/                     # Documentation
│   ├── PROJECT_CONTEXT.md    # Project goals and status
│   ├── FEATURES.md           # Feature roadmap
│   └── learning_notes/       # RL concepts and lessons learned
├── experiments/              # Saved experiments and results
│   ├── gridworld/            # GridWorld experiment results
│   └── solitaire/            # Solitaire experiment results
└── pyproject.toml            # Project configuration
```

## 🛠️ Development Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Type check
uv run mypy src/

# Run all quality checks
uv run ruff check . && uv run ruff format . && uv run mypy src/ && uv run pytest

# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files

# Update dependencies
uv lock
uv sync
```

## 📝 Documentation Workflow

### Pre-Commit Documentation Check

When committing code changes, you'll be prompted:

```
⚠️  CODE CHANGES DETECTED - DOCUMENTATION CHECK
You're committing code changes. Have you updated the documentation?

Relevant docs to consider:
  • docs/PROJECT_CONTEXT.md  - Project goals and current status
  • docs/FEATURES.md         - Feature status and roadmap
  • docs/ARCHITECTURE.md     - Technical decisions
  • README.md                - User-facing documentation

Docs updated or not needed? (yes/no):
```

This ensures documentation stays in sync with code - crucial for Claude Code effectiveness!

### Creating Feature Documentation

For non-trivial features:

```bash
# Copy the template
cp docs/templates/FEATURE_TEMPLATE.md docs/features/FEATURE-001-my-feature.md

# Fill it out (helps CC understand your goals)
# Implement the feature
# Update the feature doc as you go
# Mark it complete when done
```

### Creating Requirements Documentation

For major features or new projects:

```bash
# Copy the template
cp docs/templates/REQUIREMENTS_TEMPLATE.md docs/requirements/REQ-my-project.md

# Work with Claude Code to fill it out
# Use it as source of truth during implementation
```

## 🎨 Customization

### Code Quality Tools

Edit in [`pyproject.toml`](pyproject.toml):
- **Ruff**: `[tool.ruff]` section
- **mypy**: `[tool.mypy]` section
- **pytest**: `[tool.pytest.ini_options]` section

### Pre-commit Hooks

Edit [`.pre-commit-config.yaml`](.pre-commit-config.yaml) to add/remove hooks.

### CI/CD

Edit [`.github/workflows/ci.yml`](.github/workflows/ci.yml) to customize:
- Python versions tested
- Additional checks
- Deployment steps

## 🤝 Template for GitHub

### Making This a Template Repository

1. Go to repository Settings
2. Check "Template repository"
3. Users can now click "Use this template" to create new projects

### Using as a Template

When using this template:
1. Click "Use this template" → "Create a new repository"
2. Follow the Quick Start steps above
3. Customize for your project
4. Start building with Claude Code!

## 💡 Use Cases

This template is perfect for:

- **Pet Projects**: Quick experimentation with proper structure
- **Learning Projects**: Document what you learn as you go
- **POCs**: Professional structure for proof of concepts
- **Coding Agent Projects**: Maximum effectiveness with Claude Code
- **Portfolio Projects**: Production-quality setup from day one

## 📚 Additional Resources

- [uv documentation](https://github.com/astral-sh/uv)
- [Ruff documentation](https://docs.astral.sh/ruff/)
- [pytest documentation](https://docs.pytest.org/)
- [Claude Code documentation](https://claude.ai/claude-code)

## 🙏 Philosophy

This template is built on these principles:

1. **Documentation is for AI assistants too** - Not just humans
2. **Quality gates help, not hinder** - Automated checks catch issues early
3. **Templates reduce friction** - Structured planning helps execution
4. **Context preservation** - Future you (and future CC) will thank you

## 📄 License

This template is provided as-is for personal and commercial use. Customize as needed!

---

**Ready to build something amazing?** Fill out the docs, fire up Claude Code, and start coding! 🚀
