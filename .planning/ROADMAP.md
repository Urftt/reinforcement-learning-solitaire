# Roadmap: GridWorld RL Learning Environment

## Overview

This roadmap delivers a modern web-based interface for experimenting with reinforcement learning algorithms on GridWorld. Starting with core infrastructure that enables real-time training visualization, adding learning metrics to track progress, and culminating in advanced visualizations that reveal what the agent learned. Each phase builds on the previous, creating a complete feedback loop for hands-on RL exploration.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Web Infrastructure & Core Loop** - Web interface with real-time training and parameter control
- [x] **Phase 2: Learning Metrics Dashboard** - Track learning progress through curves and metrics
- [ ] **Phase 3: Advanced Visualization** - Visualize what agent learned (Q-values and policy)

## Phase Details

### Phase 1: Web Infrastructure & Core Loop
**Goal**: User can train Q-learning agent via web interface and see it learn in real-time
**Depends on**: Nothing (first phase)
**Requirements**: WEB-01, WEB-02, WEB-03, WEB-04, TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04, TRAIN-05, TRAIN-06, PARAM-01, PARAM-02, PARAM-03, PARAM-04, PARAM-05, VIZ-01, VIZ-02, VIZ-03, VIZ-04, QL-01, QL-02, QL-03, QL-04, QL-05
**Success Criteria** (what must be TRUE):
  1. User accesses GridWorld at localhost URL and sees grid with agent
  2. User starts training, adjusts learning rate, and sees training begin
  3. Agent position updates in real-time as training progresses
  4. User stops training and training halts immediately
  5. Training parameters are visible and editable before each run
**Plans**: 4 plans

Plans:
- [x] 01-01-PLAN.md — Backend FastAPI server + Q-learning agent implementation
- [x] 01-02-PLAN.md — Frontend Canvas grid renderer + parameter controls UI
- [x] 01-03-PLAN.md — Async training loop + WebSocket integration
- [x] 01-04-PLAN.md — End-to-end verification checkpoint

### Phase 2: Learning Metrics Dashboard
**Goal**: User can track learning progress through metrics and curves
**Depends on**: Phase 1
**Requirements**: METRIC-01, METRIC-02, METRIC-03, METRIC-04, METRIC-05
**Success Criteria** (what must be TRUE):
  1. User sees episode reward plotted in real-time learning curve during training
  2. Learning curve updates smoothly without blocking training performance
  3. Current reward and rolling average are displayed and update each episode
  4. Metrics persist across page refreshes during active training session
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — Backend metrics emission + frontend data layer (IndexedDB, statistics)
- [x] 02-02-PLAN.md — Chart.js visualization, statistics panel, export/clear controls

### Phase 3: Advanced Visualization
**Goal**: User can visualize what the agent learned (Q-values and policy)
**Depends on**: Phase 2
**Requirements**: QVAL-01, QVAL-02, QVAL-03, QVAL-04, POL-01, POL-02, POL-03, POL-04
**Success Criteria** (what must be TRUE):
  1. User views Q-value heatmap showing learned state values
  2. Q-values update in real-time as agent continues learning
  3. User views policy arrows showing best action per state
  4. User can toggle Q-value and policy displays on/off independently
**Plans**: TBD

Plans:
- [ ] TBD during phase planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Web Infrastructure & Core Loop | 4/4 | ✓ Complete | 2026-01-31 |
| 2. Learning Metrics Dashboard | 2/2 | ✓ Complete | 2026-02-01 |
| 3. Advanced Visualization | 0/TBD | Not started | - |
