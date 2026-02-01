# Phase 3: Advanced Visualization - Research

**Researched:** 2026-02-01
**Domain:** Canvas-based Q-value heatmap overlays, policy arrow visualization, and toggle switch UI controls
**Confidence:** HIGH

## Summary

Phase 3 requires adding two visual overlays to the existing GridRenderer canvas: a Q-value heatmap showing learned state values with a red-to-green gradient, and policy arrows showing the best action direction for each state. Both overlays update in real-time as training progresses and can be independently toggled on/off via modern CSS toggle switches in the sidebar.

The existing canvas rendering infrastructure (GridRenderer class with requestAnimationFrame loop) is well-suited for this phase. The approach is to extend the render() method with additional overlay layers drawn after the base grid but before the agent/goal. The Q-table data must be sent from the backend via WebSocket after each episode, and the frontend stores it for rendering.

The key implementation patterns are:
1. **Layered canvas rendering:** Draw heatmap layer, then policy arrows, then existing elements (obstacles, goal, agent)
2. **RGB color interpolation:** Use linear interpolation between red [255,0,0] and green [0,255,0] based on normalized Q-value
3. **Triangle arrow rendering:** Use canvas path API (beginPath, moveTo, lineTo, fill) to draw direction indicators
4. **Toggle switches:** Pure CSS implementation using hidden checkbox with styled label/pseudo-elements
5. **Q-table WebSocket transmission:** Add `episode_complete` message field or new `qtable_update` message type

**Primary recommendation:** Extend the existing GridRenderer class with renderHeatmapOverlay() and renderPolicyArrows() methods called from render(). Send Q-table snapshot from backend after each episode. Use pure CSS toggle switches matching existing UI styling. Color scale uses linear RGB interpolation with legend drawn to the right of the grid.

## Standard Stack

The phase uses only existing technologies from Phase 1 - no new libraries required.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Canvas API | Native | Heatmap cells, policy arrows, color legend | Already used in Phase 1 GridRenderer; efficient for layered overlays |
| WebSocket API | Native | Q-table data transmission from backend | Already established in Phase 1 |
| CSS Transitions | Native | Toggle switch animations | No external library needed for simple sliding toggle |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| NumPy | Existing | Q-table to JSON serialization | Already in backend for Q-table operations |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Canvas heatmap | Separate overlay canvas | Two canvases add complexity; single canvas with layered rendering is simpler |
| CSS toggle | Third-party toggle library | Unnecessary dependency; native CSS toggle is sufficient |
| RGB interpolation | color.js library | Overkill for simple red-green gradient; vanilla JS is faster and smaller |
| Full Q-table per episode | Q-table diff/delta | Adds complexity; full snapshot is small (5x5x4 = 100 floats = ~1KB) |

**Installation:**
```bash
# No new dependencies required
```

## Architecture Patterns

### Recommended Project Structure
```
static/
├── app.js                 # Extended GridRenderer class
│   ├── GridRenderer       # Existing class
│   │   ├── constructor()
│   │   ├── update()
│   │   ├── render()       # MODIFY: Add overlay calls
│   │   ├── renderHeatmapOverlay()   # NEW
│   │   ├── renderPolicyArrows()     # NEW
│   │   ├── renderColorLegend()      # NEW
│   │   ├── interpolateColor()       # NEW helper
│   │   └── startAnimationLoop()
│   └── (existing classes)
├── styles.css             # Add toggle switch styles
└── index.html             # Add toggle controls to sidebar
```

### Pattern 1: Layered Canvas Rendering

**What:** Render overlays in specific z-order: background, heatmap, arrows, grid lines, obstacles, goal, agent. Each layer is drawn by a dedicated method.

**When to use:** Any time you need multiple visual layers on a single canvas that must be composited correctly.

**Example:**
```javascript
// Source: Canvas layering best practice
render() {
    // Clear canvas
    this.ctx.fillStyle = '#f5f5f5';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Layer 1: Heatmap (if enabled)
    if (this.showHeatmap) {
        this.renderHeatmapOverlay();
    }

    // Layer 2: Grid lines (draw over heatmap)
    this.renderGridLines();

    // Layer 3: Policy arrows (if enabled)
    if (this.showPolicyArrows) {
        this.renderPolicyArrows();
    }

    // Layer 4: Obstacles
    this.renderObstacles();

    // Layer 5: Trail effect
    this.renderTrail();

    // Layer 6: Goal
    this.renderGoal();

    // Layer 7: Agent (top layer)
    this.renderAgent();
}
```

### Pattern 2: Linear RGB Color Interpolation for Heatmap

**What:** Interpolate between two RGB colors based on a normalized value (0-1). For Q-value heatmaps, 0 = red (low), 1 = green (high).

**When to use:** When mapping continuous values to a gradient color scale.

**Example:**
```javascript
// Source: Linear color interpolation pattern
// https://dev.to/ndesmic/linear-color-gradients-from-scratch-1a0e

interpolateColor(value) {
    // value: 0.0 to 1.0
    // 0.0 = red (255, 0, 0)
    // 1.0 = green (0, 255, 0)
    const red = Math.round(255 * (1 - value));
    const green = Math.round(255 * value);
    return `rgb(${red}, ${green}, 0)`;
}

renderHeatmapOverlay() {
    if (!this.qTable) return;

    const { min, max } = this.getQTableRange();

    for (let x = 0; x < this.gridSize; x++) {
        for (let y = 0; y < this.gridSize; y++) {
            // Get max Q-value for this state (state value)
            const maxQ = Math.max(...this.qTable[x][y]);

            // Normalize to 0-1 range
            const normalized = (max === min) ? 0.5 : (maxQ - min) / (max - min);

            // Draw colored cell
            this.ctx.fillStyle = this.interpolateColor(normalized);
            this.ctx.globalAlpha = 0.6; // Semi-transparent overlay
            this.ctx.fillRect(
                x * this.cellSize,
                y * this.cellSize,
                this.cellSize,
                this.cellSize
            );
            this.ctx.globalAlpha = 1.0;

            // Draw Q-value text
            this.ctx.fillStyle = '#000';
            this.ctx.font = '10px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(
                maxQ.toFixed(1),
                (x + 0.5) * this.cellSize,
                (y + 0.5) * this.cellSize + 4
            );
        }
    }
}

getQTableRange() {
    let min = Infinity;
    let max = -Infinity;
    for (let x = 0; x < this.gridSize; x++) {
        for (let y = 0; y < this.gridSize; y++) {
            const maxQ = Math.max(...this.qTable[x][y]);
            min = Math.min(min, maxQ);
            max = Math.max(max, maxQ);
        }
    }
    return { min, max };
}
```

### Pattern 3: Triangle Arrow Rendering for Policy

**What:** Draw triangular arrows pointing in the direction of the best action for each state. Handle ties by drawing multiple arrows.

**When to use:** Visualizing optimal policy on a grid-based environment.

**Example:**
```javascript
// Source: MDN Canvas tutorial - drawing triangles
// https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Drawing_shapes

renderPolicyArrows() {
    if (!this.qTable) return;

    const arrowSize = this.cellSize * 0.25; // Triangle size relative to cell

    for (let x = 0; x < this.gridSize; x++) {
        for (let y = 0; y < this.gridSize; y++) {
            const qValues = this.qTable[x][y];
            const maxQ = Math.max(...qValues);

            // Skip unexplored states (all zeros or uninitialized)
            if (maxQ === 0 && Math.min(...qValues) === 0) continue;

            // Find all actions with max Q-value (handle ties)
            const bestActions = [];
            for (let a = 0; a < 4; a++) {
                if (qValues[a] === maxQ) bestActions.push(a);
            }

            const centerX = (x + 0.5) * this.cellSize;
            const centerY = (y + 0.5) * this.cellSize;

            this.ctx.fillStyle = '#333'; // Dark gray for contrast

            for (const action of bestActions) {
                this.drawTriangle(centerX, centerY, action, arrowSize);
            }
        }
    }
}

drawTriangle(cx, cy, direction, size) {
    // direction: 0=up, 1=down, 2=left, 3=right
    const rotations = [
        -Math.PI / 2,  // Up
        Math.PI / 2,   // Down
        Math.PI,       // Left
        0              // Right (default: pointing right)
    ];

    const angle = rotations[direction];

    this.ctx.save();
    this.ctx.translate(cx, cy);
    this.ctx.rotate(angle);

    // Draw equilateral triangle pointing right
    this.ctx.beginPath();
    this.ctx.moveTo(size, 0);                    // Point
    this.ctx.lineTo(-size / 2, -size * 0.6);     // Top-left
    this.ctx.lineTo(-size / 2, size * 0.6);      // Bottom-left
    this.ctx.closePath();
    this.ctx.fill();

    this.ctx.restore();
}
```

### Pattern 4: Color Bar Legend

**What:** Draw a vertical gradient bar to the right of the grid showing the color mapping from min to max Q-value.

**When to use:** When users need to understand the meaning of heatmap colors.

**Example:**
```javascript
// Source: Canvas gradient rendering pattern

renderColorLegend() {
    if (!this.qTable) return;

    const { min, max } = this.getQTableRange();
    const legendWidth = 20;
    const legendHeight = this.canvas.height - 40;
    const legendX = this.canvas.width + 10;
    const legendY = 20;

    // Draw gradient bar
    for (let i = 0; i < legendHeight; i++) {
        const normalized = 1 - (i / legendHeight); // Top = max, bottom = min
        this.ctx.fillStyle = this.interpolateColor(normalized);
        this.ctx.fillRect(legendX, legendY + i, legendWidth, 1);
    }

    // Draw border
    this.ctx.strokeStyle = '#333';
    this.ctx.strokeRect(legendX, legendY, legendWidth, legendHeight);

    // Draw min/max labels
    this.ctx.fillStyle = '#333';
    this.ctx.font = '10px sans-serif';
    this.ctx.textAlign = 'left';
    this.ctx.fillText(max.toFixed(2), legendX + legendWidth + 5, legendY + 10);
    this.ctx.fillText(min.toFixed(2), legendX + legendWidth + 5, legendY + legendHeight);
}
```

### Pattern 5: CSS Toggle Switch

**What:** Pure CSS toggle switch using hidden checkbox input with styled label and pseudo-elements.

**When to use:** On/off controls in settings panels.

**Example:**
```css
/* Source: W3Schools toggle switch */
/* https://www.w3schools.com/howto/howto_css_switch.asp */

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 26px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.3s;
    border-radius: 26px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 20px;
    width: 20px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: #4caf50;
}

input:checked + .toggle-slider:before {
    transform: translateX(24px);
}
```

```html
<div class="toggle-group">
    <label class="toggle-switch">
        <input type="checkbox" id="heatmap-toggle">
        <span class="toggle-slider"></span>
    </label>
    <span class="toggle-label">Q-Value Heatmap</span>
</div>
```

### Pattern 6: Q-Table WebSocket Transmission

**What:** Send the full Q-table from backend to frontend after each episode for overlay rendering.

**When to use:** When frontend needs Q-table data for visualization.

**Example:**
```python
# Backend: src/gridworld/server.py
# Add q_table to episode_complete event

await manager.broadcast({
    "type": "episode_complete",
    "data": {
        "episode": episode + 1,
        "reward": total_reward,
        "steps": step,
        "epsilon": float(agent.epsilon),
        "q_table": agent.q_table.tolist(),  # NEW: Include Q-table
    },
})
```

```javascript
// Frontend: app.js
// Handle Q-table in episode_complete handler

wsClient.on('episode_complete', async (data) => {
    // ... existing metrics handling ...

    // Store Q-table for visualization
    if (data.q_table) {
        renderer.setQTable(data.q_table);
    }
});

// GridRenderer method
setQTable(qTable) {
    this.qTable = qTable;
}
```

### Anti-Patterns to Avoid

- **Drawing overlays on separate canvas:** Adds complexity with canvas stacking and synchronization. Single canvas with layered rendering is simpler.

- **Recreating Q-table array every frame:** Store Q-table reference and only update when new data arrives, not every render frame.

- **Using string concatenation for CSS colors:** Use template literals or RGB function for performance and readability.

- **Hardcoding grid positions for arrows:** Use relative positioning (cellSize * x) to support future grid size changes.

- **Sending Q-table every step:** Excessive bandwidth. Send only on episode completion.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Color gradient between red/green | Color library, complex HSL | Simple RGB linear interpolation | Two-color gradient is trivial; lerp formula is 3 lines of code |
| Toggle switch | Custom JavaScript state | CSS checkbox + styling | CSS handles all state; JS only reads checkbox.checked |
| Canvas text centering | Manual width calculations | ctx.textAlign = 'center' + x position | Canvas API handles text measurement internally |
| Q-table normalization | Separate normalization pass | Inline min/max calculation | Small grid (5x5x4) makes O(n) scan negligible per frame |

**Key insight:** This phase primarily involves canvas rendering patterns that are well-documented in MDN. The challenge is layering and integration, not implementing novel algorithms. Stick to established canvas patterns.

## Common Pitfalls

### Pitfall 1: Incorrect Z-Order Causing Hidden Elements

**What goes wrong:** Heatmap colors render over the agent, making the agent invisible. Or policy arrows render under the heatmap, making them invisible.

**Why it happens:** Canvas has no z-index; render order determines visibility. Later draw calls appear on top.

**How to avoid:**
1. Define explicit layer order: background -> heatmap -> grid -> arrows -> obstacles -> goal -> agent
2. Create separate render methods for each layer
3. Call render methods in correct order from main render()

**Warning signs:**
- Agent disappears when heatmap is enabled
- Arrows not visible when both overlays are enabled
- Goal hidden by heatmap color

### Pitfall 2: Performance Degradation from Per-Pixel Operations

**What goes wrong:** Iterating pixel-by-pixel for heatmap causes frame rate drops.

**Why it happens:** Canvas 2D context is fast for shape operations but slow for pixel manipulation. Drawing individual pixels is O(width * height) per frame.

**How to avoid:**
1. Use fillRect() for each cell (one draw call per cell)
2. Do NOT use getImageData/putImageData for heatmap coloring
3. Cache Q-table range calculations if they don't change between frames

**Warning signs:**
- FPS drops from 60 to <30 when heatmap is enabled
- DevTools Performance tab shows long paint times
- Visible lag when toggling heatmap on

### Pitfall 3: Text Rendering Blurriness on Retina Displays

**What goes wrong:** Q-value text in cells appears blurry or pixelated on high-DPI screens.

**Why it happens:** Canvas renders at device pixel ratio 1 by default. Retina displays have ratio 2 or 3, causing upscaling blur.

**How to avoid:**
1. Scale canvas using devicePixelRatio:
```javascript
const dpr = window.devicePixelRatio || 1;
canvas.width = width * dpr;
canvas.height = height * dpr;
canvas.style.width = width + 'px';
canvas.style.height = height + 'px';
ctx.scale(dpr, dpr);
```
2. Or: Accept slight blur for simplicity (localhost tool, not production)

**Warning signs:**
- Text looks fuzzy compared to surrounding HTML text
- Numbers in cells are hard to read
- Only happens on Mac/Retina displays

### Pitfall 4: Toggle State Not Persisting Across Page Refresh

**What goes wrong:** User enables heatmap, refreshes page, heatmap is disabled again.

**Why it happens:** Toggle state is only in JavaScript memory. Page refresh resets to defaults (both OFF per CONTEXT.md).

**How to avoid:**
1. Per CONTEXT.md, both toggles default to OFF - this is expected behavior
2. If persistence is desired: save toggle state to localStorage on change
3. Read from localStorage on page load and set checkbox checked property

**Warning signs:**
- User complaint: "I have to re-enable overlays every time"
- Toggle visually resets on refresh

### Pitfall 5: Q-Table Data Stale After Training Stop

**What goes wrong:** User stops training, Q-table overlay shows old values. User expects to see "last known state" but instead sees initial zeros.

**Why it happens:** Training stop might reset agent or Q-table in backend. Or frontend doesn't retain Q-table reference.

**How to avoid:**
1. Per CONTEXT.md: "Keep showing last state when training is paused"
2. Do NOT clear renderer.qTable on training_stopped event
3. Only reset Q-table on explicit "reset" command
4. On page refresh: reload Q-table if load_qtable endpoint returns saved Q-table

**Warning signs:**
- Heatmap goes blank after stopping training
- User loses visual context of learned values

### Pitfall 6: Arrow Overlap in Small Cells

**What goes wrong:** When multiple actions are tied, drawing multiple arrows causes visual clutter. Arrows overlap and become unreadable.

**Why it happens:** Triangle size is fixed relative to cell, but multiple triangles in same cell overlap at center.

**How to avoid:**
1. Offset tied arrows slightly from center (radial arrangement)
2. Or: Use smaller arrow size when ties exist
3. Or: Draw single arrow with multiple heads (more complex)
4. For 5x5 grid with 50px cells, keep arrow size at ~12px (0.25 * cellSize)

**Warning signs:**
- Cells with tied actions look like a single blob
- Can't tell which directions are tied
- Arrows overlap with Q-value text

## Code Examples

Verified patterns from official sources:

### Complete GridRenderer Extension

```javascript
// Source: Canvas API patterns from MDN
// Extended GridRenderer class

class GridRenderer {
    constructor(canvasId, gridSize, cellSize = 50) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = gridSize;
        this.cellSize = cellSize;

        this.canvas.width = gridSize * cellSize;
        this.canvas.height = gridSize * cellSize;

        this.state = {
            agent_pos: [0, 0],
            goal_pos: [gridSize - 1, gridSize - 1],
            obstacles: [[1, 1], [2, 2], [3, 1]],
            trail: []
        };

        // Visualization state (NEW)
        this.qTable = null;
        this.showHeatmap = false;
        this.showPolicyArrows = false;

        this.maxTrailLength = 20;
    }

    setQTable(qTable) {
        this.qTable = qTable;
    }

    setShowHeatmap(show) {
        this.showHeatmap = show;
    }

    setShowPolicyArrows(show) {
        this.showPolicyArrows = show;
    }

    // Color interpolation: red (low) to green (high)
    interpolateColor(value) {
        // value: 0.0 = red, 1.0 = green
        const red = Math.round(255 * (1 - value));
        const green = Math.round(255 * value);
        return `rgb(${red}, ${green}, 0)`;
    }

    getQTableRange() {
        if (!this.qTable) return { min: 0, max: 0 };
        let min = Infinity;
        let max = -Infinity;
        for (let x = 0; x < this.gridSize; x++) {
            for (let y = 0; y < this.gridSize; y++) {
                const maxQ = Math.max(...this.qTable[x][y]);
                min = Math.min(min, maxQ);
                max = Math.max(max, maxQ);
            }
        }
        return { min, max };
    }

    renderHeatmapOverlay() {
        if (!this.qTable) return;

        const { min, max } = this.getQTableRange();

        for (let x = 0; x < this.gridSize; x++) {
            for (let y = 0; y < this.gridSize; y++) {
                const maxQ = Math.max(...this.qTable[x][y]);
                const normalized = (max === min) ? 0.5 : (maxQ - min) / (max - min);

                // Draw colored cell
                this.ctx.fillStyle = this.interpolateColor(normalized);
                this.ctx.globalAlpha = 0.5;
                this.ctx.fillRect(
                    x * this.cellSize,
                    y * this.cellSize,
                    this.cellSize,
                    this.cellSize
                );
                this.ctx.globalAlpha = 1.0;

                // Draw Q-value text
                this.ctx.fillStyle = '#000';
                this.ctx.font = 'bold 11px sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.textBaseline = 'middle';
                this.ctx.fillText(
                    maxQ.toFixed(1),
                    (x + 0.5) * this.cellSize,
                    (y + 0.5) * this.cellSize
                );
            }
        }
    }

    renderPolicyArrows() {
        if (!this.qTable) return;

        const arrowSize = this.cellSize * 0.2;

        for (let x = 0; x < this.gridSize; x++) {
            for (let y = 0; y < this.gridSize; y++) {
                const qValues = this.qTable[x][y];
                const maxQ = Math.max(...qValues);

                // Skip unexplored states
                if (maxQ === 0 && Math.min(...qValues) === 0) continue;

                // Find best actions (handle ties)
                const bestActions = qValues
                    .map((q, i) => ({ q, i }))
                    .filter(a => a.q === maxQ)
                    .map(a => a.i);

                const centerX = (x + 0.5) * this.cellSize;
                const centerY = (y + 0.5) * this.cellSize;

                this.ctx.fillStyle = '#333';

                for (const action of bestActions) {
                    this.drawArrow(centerX, centerY, action, arrowSize);
                }
            }
        }
    }

    drawArrow(cx, cy, direction, size) {
        // 0=up, 1=down, 2=left, 3=right
        const angles = [-Math.PI / 2, Math.PI / 2, Math.PI, 0];
        const angle = angles[direction];

        // Offset from center based on direction
        const offset = this.cellSize * 0.25;
        const offsets = [
            [0, -offset],  // up
            [0, offset],   // down
            [-offset, 0],  // left
            [offset, 0]    // right
        ];

        const [ox, oy] = offsets[direction];

        this.ctx.save();
        this.ctx.translate(cx + ox, cy + oy);
        this.ctx.rotate(angle);

        this.ctx.beginPath();
        this.ctx.moveTo(size, 0);
        this.ctx.lineTo(-size * 0.5, -size * 0.6);
        this.ctx.lineTo(-size * 0.5, size * 0.6);
        this.ctx.closePath();
        this.ctx.fill();

        this.ctx.restore();
    }

    render() {
        // Clear
        this.ctx.fillStyle = '#f5f5f5';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Heatmap overlay (under grid lines)
        if (this.showHeatmap && this.qTable) {
            this.renderHeatmapOverlay();
        }

        // Grid lines
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= this.gridSize; i++) {
            const pos = i * this.cellSize;
            this.ctx.beginPath();
            this.ctx.moveTo(pos, 0);
            this.ctx.lineTo(pos, this.canvas.height);
            this.ctx.stroke();
            this.ctx.beginPath();
            this.ctx.moveTo(0, pos);
            this.ctx.lineTo(this.canvas.width, pos);
            this.ctx.stroke();
        }

        // Policy arrows (after grid lines, before obstacles)
        if (this.showPolicyArrows && this.qTable) {
            this.renderPolicyArrows();
        }

        // Obstacles
        this.ctx.fillStyle = '#333';
        for (const [x, y] of this.state.obstacles) {
            this.ctx.fillRect(
                x * this.cellSize,
                y * this.cellSize,
                this.cellSize,
                this.cellSize
            );
        }

        // Trail
        for (let i = 0; i < this.state.trail.length; i++) {
            const [x, y] = this.state.trail[i];
            const opacity = (i + 1) / this.state.trail.length * 0.3;
            this.ctx.fillStyle = `rgba(100, 150, 255, ${opacity})`;
            this.ctx.fillRect(
                x * this.cellSize + 5,
                y * this.cellSize + 5,
                this.cellSize - 10,
                this.cellSize - 10
            );
        }

        // Goal
        const [gx, gy] = this.state.goal_pos;
        this.ctx.fillStyle = '#4caf50';
        this.ctx.beginPath();
        this.ctx.arc(
            (gx + 0.5) * this.cellSize,
            (gy + 0.5) * this.cellSize,
            this.cellSize / 3,
            0,
            Math.PI * 2
        );
        this.ctx.fill();

        // Agent
        if (this.state.agent_pos) {
            const [ax, ay] = this.state.agent_pos;
            this.ctx.fillStyle = '#ff6b6b';
            this.ctx.beginPath();
            this.ctx.arc(
                (ax + 0.5) * this.cellSize,
                (ay + 0.5) * this.cellSize,
                this.cellSize / 2.5,
                0,
                Math.PI * 2
            );
            this.ctx.fill();
        }
    }
}
```

### Toggle Switch HTML/CSS

```html
<!-- In sidebar, after qtable-buttons section -->
<div class="visualization-toggles">
    <h3>Visualization</h3>

    <div class="toggle-group">
        <label class="toggle-switch">
            <input type="checkbox" id="heatmap-toggle">
            <span class="toggle-slider"></span>
        </label>
        <span class="toggle-label">Q-Value Heatmap</span>
    </div>

    <div class="toggle-group">
        <label class="toggle-switch">
            <input type="checkbox" id="policy-toggle">
            <span class="toggle-slider"></span>
        </label>
        <span class="toggle-label">Policy Arrows</span>
    </div>
</div>
```

```css
/* Toggle switch styles */
.visualization-toggles {
    margin-top: 1.2rem;
    padding-top: 1rem;
    border-top: 1px solid #e0e0e0;
}

.visualization-toggles h3 {
    font-size: 1.1rem;
    font-weight: 500;
    margin-bottom: 0.8rem;
    color: #333;
}

.toggle-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.6rem;
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.3s;
    border-radius: 24px;
}

.toggle-slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 3px;
    bottom: 3px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
}

input:checked + .toggle-slider {
    background-color: #4caf50;
}

input:checked + .toggle-slider:before {
    transform: translateX(20px);
}

.toggle-label {
    font-size: 0.9rem;
    color: #555;
}
```

### Toggle Event Handlers

```javascript
// In DOMContentLoaded event handler

// Visualization toggle event handlers
document.getElementById('heatmap-toggle').addEventListener('change', (e) => {
    renderer.setShowHeatmap(e.target.checked);
});

document.getElementById('policy-toggle').addEventListener('change', (e) => {
    renderer.setShowPolicyArrows(e.target.checked);
});

// Update episode_complete handler to store Q-table
wsClient.on('episode_complete', async (data) => {
    // ... existing metrics handling ...

    // Store Q-table for visualization
    if (data.q_table) {
        renderer.setQTable(data.q_table);
    }
});
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate overlay canvas | Single canvas with layered rendering | 2020s | Simpler code, no canvas synchronization issues |
| DOM-based heatmap (divs) | Canvas fillRect() per cell | 2015+ | Dramatically faster rendering (60fps capable) |
| HSL color interpolation | Direct RGB interpolation | Ongoing | RGB simpler for two-color gradients; HSL better for rainbow |
| Custom toggle JS | CSS-only checkbox styling | 2020s | Simpler, no state management bugs, better accessibility |

**Deprecated/outdated:**
- **DOM grid overlays:** Manipulating div elements for heatmap is too slow for real-time updates
- **Canvas pixel manipulation (getImageData/putImageData):** Unnecessary for cell-based heatmaps; use fillRect
- **jQuery for toggle handling:** Plain JavaScript addEventListener is sufficient

## Open Questions

1. **Color Bar Legend Placement**
   - What we know: CONTEXT.md says "Include color bar legend showing min/max value mapping" with Claude's discretion for placement
   - What's unclear: Whether legend should be inside canvas (requires canvas resize) or outside (separate element)
   - Recommendation: Place legend outside canvas as a separate DOM element to avoid resizing complexity. Draw with CSS gradient or small dedicated canvas.

2. **Q-Table Load on Page Refresh**
   - What we know: CONTEXT.md says "Reload overlays from Q-table on page refresh if Q-table is loaded"
   - What's unclear: How to detect if Q-table is available on page load (agent not yet created)
   - Recommendation: After WebSocket connects, send "get_qtable" command. Backend responds with current Q-table if agent exists, or null. Frontend renders overlay if data available.

3. **Number Formatting for Q-Values**
   - What we know: CONTEXT.md leaves decimal places to Claude's discretion
   - What's unclear: Whether 1 decimal place is sufficient for user understanding
   - Recommendation: Use 1 decimal place (toFixed(1)) to keep text compact in cells. If user feedback requests more precision, increase to 2.

## Sources

### Primary (HIGH confidence)
- [MDN Canvas Tutorial - Drawing Shapes](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Drawing_shapes) - Official reference for canvas path API, triangle drawing
- [W3Schools CSS Toggle Switch](https://www.w3schools.com/howto/howto_css_switch.asp) - Standard toggle switch CSS pattern
- [DEV.to Linear Color Gradients](https://dev.to/ndesmic/linear-color-gradients-from-scratch-1a0e) - RGB interpolation formula explanation

### Secondary (MEDIUM confidence)
- [CodeSignal RL Visualization Course](https://codesignal.com/learn/courses/game-on-integrating-rl-agents-with-environments/lessons/visualizing-policies-and-value-functions-in-reinforcement-learning) - Q-value heatmap and policy arrow patterns for RL
- [TinyRL GitHub](https://github.com/parasdahal/tinyrl) - Interactive RL visualization reference (D3-based but concepts apply)
- [FreeFrontend CSS Toggle Switches](https://freefrontend.com/css-toggle-switches/) - Toggle switch design variations

### Tertiary (LOW confidence)
- [simpleheat GitHub](https://github.com/mourner/simpleheat) - Canvas heatmap library (reference for patterns, not used directly)
- [Heatmap.js](http://csn.gps.caltech.edu/Events/heatmap.js-master/website/) - Gradient colorization approach reference

## Metadata

**Confidence breakdown:**
- **Standard Stack:** HIGH - Uses only existing Canvas API from Phase 1; no new dependencies
- **Architecture Patterns:** HIGH - Canvas layering and toggle CSS are well-documented standards
- **Code Examples:** HIGH - Derived from MDN official docs and verified patterns
- **Pitfalls:** HIGH - Based on common canvas rendering issues documented in tutorials

**Research date:** 2026-02-01
**Valid until:** 2026-03-01 (Canvas API and CSS are stable; patterns unlikely to change)

**Applicability:**
- This research is specific to 5x5 GridWorld with 4 actions (up/down/left/right)
- Q-table size is small (100 floats), making full transmission per episode feasible
- Localhost-only deployment means WebSocket bandwidth is not a constraint
- Toggle states default to OFF per CONTEXT.md requirements
