# GridWorld RL Learning Environment

## What This Is

A web-based GridWorld environment for learning reinforcement learning concepts through hands-on experimentation. Features real-time training visualization, learning metrics dashboard, and Q-value/policy visualizations that make RL concepts concrete and intuitive.

## Core Value

A modern web interface where I can experiment with RL algorithms, adjust parameters, and see learning happen in real-time through visualizations and metrics - making RL concepts concrete through hands-on exploration.

## Requirements

### Validated

<!-- Shipped and confirmed valuable -->

- ✓ GridWorld environment (Gymnasium-compliant) — existing
- ✓ Multiple difficulty levels (easy, medium, hard presets) — existing
- ✓ Terminal and Tkinter play modes — existing
- ✓ Test suite with 30+ environment tests — existing
- ✓ Grid rendering with obstacles, goals, agent position — existing
- ✓ Episode management (reset, step, termination) — existing
- ✓ Web-based frontend (localhost, browser-based) — v1.0
- ✓ Q-learning agent implementation with persistence — v1.0
- ✓ Training interface (start/stop, adjust hyperparameters) — v1.0
- ✓ Real-time visualization of agent learning during training — v1.0
- ✓ Learning metrics dashboard (episode rewards, steps, convergence) — v1.0
- ✓ Learning curves visualization (rewards over time, rolling averages) — v1.0
- ✓ Parameter experimentation UI (learning rate, epsilon, discount factor) — v1.0
- ✓ Q-value heatmap visualization — v1.0
- ✓ Policy arrow visualization — v1.0

### Active

<!-- Future scope for continued RL learning -->

- [ ] Algorithm comparison capability (try different approaches side-by-side)
- [ ] Save/load trained agents for comparison
- [ ] SARSA algorithm implementation
- [ ] State visitation heatmap showing exploration coverage
- [ ] Animated training progress playback

### Out of Scope

- Tkinter interface improvements — replaced with web interface
- Solitaire implementation — separate future project
- Production deployment — localhost only, for personal learning
- Mobile interface — desktop browser sufficient for experimentation
- Multi-agent environments — single agent focus for learning fundamentals

## Context

**Current State (v1.0 shipped 2026-02-01):**
- ~4,031 LOC (Python, JavaScript, HTML, CSS)
- Stack: FastAPI, WebSocket, Chart.js, Canvas API, IndexedDB
- Backend: 589 lines Python (server.py, agent.py)
- Frontend: ~3,400 lines (index.html, app.js, styles.css)

**User Background:**
- Data scientist learning reinforcement learning from scratch
- No prior RL experience but strong Python/data analysis background
- Goal is educational: understand RL through hands-on experimentation

**What's Working:**
- Modern web UI for GridWorld training at localhost
- Real-time agent visualization with 60fps canvas rendering
- Learning metrics dashboard with rewards, steps, epsilon charts
- Q-value heatmap and policy arrow visualizations
- Parameter control with presets and persistence
- Q-table save/load functionality

**Learning Goals:**
- Understand how RL algorithms work through parameter tuning
- See learning curves and convergence behavior
- Build intuition for hyperparameter effects
- Compare different RL approaches empirically
- Explore additional algorithms (SARSA, DQN) for deeper understanding

## Constraints

- **Purpose**: Educational learning environment, not production system
- **Deployment**: Localhost only - no hosting/scaling requirements
- **Tech Stack**: Open to recommendations, but must integrate with existing Python/gymnasium codebase
- **Interface**: Browser-based (web), desktop focus
- **Scope**: GridWorld only (Solitaire deferred to future project)

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Web interface essential before RL work | Tkinter too frustrating for serious experimentation, modern UI needed for visualization | ✓ Good — Modern UI enables effective learning |
| Focus on Q-learning first | Simplest algorithm for learning fundamentals, proven effective for GridWorld | ✓ Good — Foundation established |
| Localhost-only deployment | Personal learning tool, no production requirements | ✓ Good — No deployment overhead |
| Per-step broadcasting (not time-based) | GridWorld episodes complete in microseconds | ✓ Good — Smooth real-time visualization |
| IndexedDB for metrics persistence | Survives page refresh, no server storage needed | ✓ Good — Simple and effective |
| Chart.js via CDN | No build step needed, simple integration | ✓ Good — Clean setup |
| Canvas + requestAnimationFrame | 60fps visualization without DOM thrashing | ✓ Good — Smooth performance |

---
*Last updated: 2026-02-01 after v1.0 milestone*
