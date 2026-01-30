# Research Summary: Web-Based RL Training Interface

**Domain:** Educational reinforcement learning experimentation and visualization
**Researched:** 2026-01-30
**Overall confidence:** HIGH

## Executive Summary

Web-based RL training interfaces for learning environments have a clear, well-established pattern: **the core value is the feedback loop**, not the prettiness. Users need to see learning happen in real-time (agent playing + metrics updating together), understand what the agent learned (Q-values and policy visualization), and experiment with parameters to build intuition. The ecosystem shows that simpler, more focused tools (TinyRL, Coach Dashboard, Beginner's RL Playground) drive deeper learning than feature-rich dashboards—complexity without clarity actively hurts understanding.

For this project, table-stakes are real-time playback + learning curves + Q-value visualization. Everything else is either nice-to-have (save/load, comparison tools) or actively harmful if done wrong (reward smoothing, complex dashboards, automated tuning that hides algorithm behavior). The biggest risk is building "too much" UI before validating that the core feedback loop works.

## Key Findings

**Stack:** Web frontend (React/Vue recommended) communicating with Python backend (Flask/FastAPI) running Gymnasium environment
**Architecture:** Client-server with WebSocket for real-time metrics, stateless training runs, clean API boundary between RL logic and UI
**Critical pitfall:** Separation of training metrics (noisy) from test metrics (clean) — showing raw reward during training leads to reward hacking and misunderstanding
**MVP scope:** 9 core features (all P1 priority): playback, controls, metrics, parameters, learning curves, Q-values, policy, grid visualization, and a test/evaluation mode

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Infrastructure & Core Feedback Loop (Blocking for RL work)
**Why first:** Cannot validate that RL works without seeing it work. The feedback loop (train → see results → adjust) is prerequisite for everything.

**What to build:**
- Backend: Flask/FastAPI + WebSocket for metrics streaming
- Frontend: Grid visualization + real-time metric display
- Training loop: Generalized interface for agents (supports future algorithm swaps)
- WebSocket streaming of: agent position, Q-values, current metrics

**Avoid:**
- Fancy UI before core works
- Multiple algorithms (focus on Q-learning only)
- Complex comparison features (unnecessary for MVP)
- Anything that hides algorithm behavior (reward smoothing, auto-tuning)

**Success criteria:**
- User can see agent training in real-time
- Adjusting learning rate immediately shows effect
- Learning curves update smoothly
- Q-value heatmap helps understand what agent learned

### Phase 2: Learning Visualization (Deepen understanding)
**Why second:** Once training works, focus on helping learners see what's happening inside.

**What to build:**
- Q-value heatmap (how good is each state?)
- Policy arrows (what action learns best in each state?)
- State visitation heatmap (which states explored?)
- Separation of train vs test metrics (rollout mode)

**Why matters:** This is where "seeing is understanding" happens. Visualizing Q-values IS understanding Q-learning.

### Phase 3: Experimentation Tools (Enable deeper learning)
**Why third:** Once learner understands basic concepts, enable systematic exploration.

**What to build:**
- Save/load trained agents
- Session-based experiment tracking
- Simple parameter sweep UI
- Side-by-side comparison of different runs

**Avoid:**
- Automated hyperparameter search (defeats learning)
- Statistical tools until learner asks for them
- Algorithm comparison before Phase 2 (too early to compare)

### Phase 4: Advanced Learning (SARSA, comparison, etc.)
**Why fourth:** Only after mastering Q-learning do other algorithms matter.

**What to build:**
- SARSA algorithm implementation
- Algorithm comparison UI
- Gradient/weight visualization (for deep RL readiness)
- Statistical confidence intervals on results

## Research Gaps Requiring Phase-Specific Deeper Investigation

### Phase 1 Investigations
- [ ] WebSocket payload size limits and update frequency optimization (how often can we stream without overwhelming browser?)
- [ ] React/Vue component architecture for real-time metric updates (what's the best way to structure this for performance?)
- [ ] Frontend library for plotting (Plotly vs Chart.js vs D3 for learning curves?)

### Phase 2 Investigations
- [ ] Color scale for heatmaps: how to color Q-values to be learner-friendly? (what range? perceptually uniform?)
- [ ] Optimal grid cell size for both visualization and interaction?
- [ ] Animation performance: can we animate policy convergence without lag?

### Phase 3+ Investigations
- [ ] Database schema for experiment tracking (SQLite sufficient for localhost, but what structure?)
- [ ] Comparison metrics: what makes a "good" comparison visualization?

These are not blockers—standard engineering decisions—but worth investigating during each phase.

## What We're Confident About

- **Core features are right:** The 9 P1 features from FEATURES.md are backed by multiple independent sources (Coach Dashboard, TinyRL, RLInspect, Beginner's RL Playground)
- **Architecture pattern is solid:** Frontend/backend separation with WebSocket for real-time metrics is industry standard (see Coach Dashboard, LiveTune)
- **Anti-patterns are clear:** Reward smoothing, automated tuning, complex UIs all documented as problematic in research
- **Educational focus is correct:** Simpler tools drive better learning than feature-rich dashboards (consistent across sources)

## What Needs Validation in Phase Implementation

- **Specific tech choices:** Flask vs FastAPI tradeoffs at localhost scale (probably doesn't matter, but worth quick test)
- **Frontend framework:** React vs Vue preference (both work; depends on team comfort)
- **Real-time update frequency:** How often to stream metrics? (15 Hz? 30 Hz? Benchmark needed)
- **Gymnasium compatibility:** Existing GridWorld is Gymnasium-compatible, but backend API design needs validation

## Quality Gate Checklist

- [x] Categories are clear (table stakes vs differentiators vs anti-features)
- [x] Features specific to RL experimentation/learning (not generic web UI)
- [x] Complexity and dependencies noted
- [x] User learning value explained for each feature
- [x] Educational design patterns identified
- [x] MVP scope defined with P1/P2/P3 prioritization
- [x] Sources cited from industry tools and research papers
- [x] Confidence levels assigned based on source types

---

*Research complete. Ready for roadmap creation.*
*Researched: 2026-01-30*
