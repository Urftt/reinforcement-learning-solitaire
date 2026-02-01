# Phase 3: Advanced Visualization - Context

**Gathered:** 2026-02-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Visualize what the agent learned through Q-value heatmaps and policy arrow overlays on the grid. Users can toggle each visualization independently and see updates in real-time during training. This phase adds visualization layers — it does not change training behavior or add new learning algorithms.

</domain>

<decisions>
## Implementation Decisions

### Q-value heatmap style
- Red-to-green gradient color scheme (red = low value, green = high value)
- Display max Q-value (state value) numerically on each cell, always visible
- Include color bar legend showing min/max value mapping
- Color intensity maps to relative Q-value within current range

### Policy arrow design
- Simple triangles pointing in best action direction
- Black/dark gray color for contrast against heatmap
- Show all tied directions when multiple actions have same max Q-value
- No arrow for unexplored states (where Q-values are zero/uninitialized)

### Toggle UX & placement
- Toggle switches (modern sliding style) in sidebar with other controls
- Both toggles default to OFF on page load
- No keyboard shortcuts — mouse/touch only
- Labels: "Q-Value Heatmap" and "Policy Arrows" (or similar)

### Real-time update behavior
- Update overlays every episode (not throttled)
- No animation — instant value changes
- Keep showing last state when training is paused
- Reload overlays from Q-table on page refresh if Q-table is loaded

### Claude's Discretion
- Exact triangle sizing relative to cell size
- Legend placement (vertical vs horizontal, left vs right of grid)
- Number formatting for Q-values (decimal places)
- Exact toggle switch styling (match existing UI)

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-advanced-visualization*
*Context gathered: 2026-02-01*
