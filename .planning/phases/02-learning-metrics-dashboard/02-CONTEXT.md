# Phase 2: Learning Metrics Dashboard - Context

**Gathered:** 2026-01-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Display real-time learning metrics through charts and statistics during training. Track episode rewards, steps per episode, and epsilon decay. Provide visual feedback on learning progress with smoothed trends and summary statistics. Export capabilities for external analysis.

</domain>

<decisions>
## Implementation Decisions

### Chart presentation
- Three separate charts: Episode rewards, Steps per episode, Epsilon value
- Each chart displays both raw episode data and rolling average trend line
- Separate chart layout (one per metric, stacked vertically)
- Charts update every episode with instant rendering (no animation)
- Auto-scroll viewport to show latest data as training progresses

### Update behavior
- Charts update every episode immediately
- Pause button to freeze chart updates while training continues
- Instant updates without animation transitions
- Viewport auto-scrolls to latest data (always shows most recent episodes)

### Data retention
- Keep full session history (unbounded episode storage)
- Persist metrics data to localStorage across page refreshes
- Manual clear button to reset all metrics data
- Export functionality: Download metrics as CSV/JSON for external analysis

### Statistics display
- Current episode metrics: Latest reward, steps, epsilon
- Running averages: Mean reward/steps over configurable window (user sets N episodes)
- Best performance: Highest reward achieved and episode number
- Statistics update every episode (synchronized with charts)

### Claude's Discretion
- Statistics layout position (above, beside, or below charts)
- Exact rolling average window defaults
- Chart library selection (Chart.js, Plotly, or canvas-based)
- CSV/JSON export format details

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches for RL dashboard visualization.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-learning-metrics-dashboard*
*Context gathered: 2026-01-31*
