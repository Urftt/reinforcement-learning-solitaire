# Phase 2: Learning Metrics Dashboard - Research

**Researched:** 2026-01-31
**Domain:** Real-time metrics visualization, time-series data storage, JavaScript charting
**Confidence:** HIGH

## Summary

Phase 2 requires building a real-time metrics dashboard that displays learning progress during RL training. Research shows the ecosystem has mature, well-established solutions for this domain. The primary decision is selecting a charting library (Chart.js recommended for simplicity and real-time support), paired with IndexedDB for persistent storage (due to localStorage's 5MB limit being insufficient for unbounded episode data). Common pitfalls center on memory management with continuous data updates and handling WebSocket backpressure to prevent data loss.

The standard approach is to:
1. Use Chart.js for incremental chart updates via the `chart.update()` method
2. Persist metrics to IndexedDB using a wrapper library like `idb`
3. Implement a rolling window for statistics to avoid unbounded array growth
4. Use simple rolling average calculations (no library needed for basic mean)
5. Manage data growth via configurable retention policies

**Primary recommendation:** Use Chart.js for all three charts with incremental data updates; store full session history in IndexedDB with manual clear option; compute rolling averages client-side; implement per-episode update frequency with update batching on the server to prevent backpressure issues.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Chart.js | 4.x | Real-time line charts with incremental updates | Most popular (2M+ weekly downloads), battle-tested for real-time updates, seamless DOM integration, built-in animation support |
| IndexedDB | Native API | Persistent metrics storage across page refreshes | Supports gigabytes of data, asynchronous (non-blocking), transactions, indexing for queries |
| idb | 8.x | Promise wrapper for IndexedDB | Significantly reduces boilerplate compared to raw IndexedDB API |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| simple-statistics | 7.x | Rolling average and statistics calculations | When custom implementations are needed; otherwise plain JS is sufficient |
| navigator.storage.estimate() | Native API | Monitor storage quota usage | Detect when approaching storage limits before QuotaExceededError |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Chart.js | ECharts | ECharts supports more data points (10M+ at 60fps) but adds complexity; Chart.js sufficient for RL metrics (typical <10k episodes) |
| Chart.js | ApexCharts | ApexCharts has cleaner real-time API but less community support; Chart.js more battle-tested |
| Chart.js | Canvas-based | Custom canvas rendering avoids library dependency but requires manual animation/interaction handling |
| IndexedDB | localStorage | localStorage limited to 5MB total (insufficient for unbounded episode storage); IndexedDB supports GBs |
| IndexedDB | Server-side persistence | Adds server complexity; localStorage-first approach works for localhost-only deployment |

**Installation:**
```bash
npm install chart.js idb simple-statistics
```

## Architecture Patterns

### Recommended Project Structure

```
src/
├── visualization/
│   ├── index.html                    # Main page with metrics containers
│   ├── app.js                        # Main entry point, orchestration
│   ├── metrics/
│   │   ├── MetricsCollector.js       # Aggregate episode data
│   │   ├── ChartManager.js           # Chart lifecycle and updates
│   │   ├── StorageManager.js         # IndexedDB operations (read/write)
│   │   └── StatisticsCalculator.js   # Rolling averages and stats
│   └── styles.css                    # Chart and metrics styling
```

### Pattern 1: Incremental Chart Updates via Chart.js

**What:** Chart.js supports adding data points to existing charts without full re-render. Call `chart.update()` to apply changes with animations.

**When to use:** Every episode, push new data point to chart and update with `chart.update()`. Do not recreate the chart object.

**Example:**
```javascript
// Source: https://www.chartjs.org/docs/latest/developers/updates.html
// Initialize once
const ctx = document.getElementById('rewardChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [1],
    datasets: [{
      label: 'Episode Reward',
      data: [0],
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.1)',
      tension: 0.1
    }, {
      label: 'Rolling Average',
      data: [0],
      borderColor: 'rgb(255, 99, 132)',
      borderDash: [5, 5]
    }]
  }
});

// Per episode: push data and update
function updateChartWithEpisode(episodeNum, reward, rollingAvg) {
  chart.data.labels.push(episodeNum);
  chart.data.datasets[0].data.push(reward);
  chart.data.datasets[1].data.push(rollingAvg);
  chart.update('none'); // 'none' skips animation for responsiveness
}
```

### Pattern 2: IndexedDB Persistence with idb Wrapper

**What:** Use `idb` library to store metrics in IndexedDB with async/await syntax. Handles transactions, error recovery automatically.

**When to use:** Save metrics after each episode completes; restore on page load if training session is still active.

**Example:**
```javascript
// Source: Web.dev storage recommendations
import { openDB } from 'idb';

const db = await openDB('metrics', 1, {
  upgrade(db) {
    if (!db.objectStoreNames.contains('episodes')) {
      const store = db.createObjectStore('episodes', { keyPath: 'episodeNum' });
      store.createIndex('timestamp', 'timestamp');
    }
  }
});

// Save episode data
async function saveEpisode(episodeNum, reward, steps, epsilon) {
  try {
    await db.add('episodes', {
      episodeNum,
      reward,
      steps,
      epsilon,
      timestamp: Date.now()
    });
  } catch (e) {
    if (e.name === 'QuotaExceededError') {
      console.error('Storage quota exceeded');
      // Trigger clear dialog or implement archival strategy
    }
  }
}

// Load all episodes on startup
async function loadMetrics() {
  return await db.getAll('episodes');
}

// Clear all metrics
async function clearAllMetrics() {
  await db.clear('episodes');
}
```

### Pattern 3: Rolling Average Calculation

**What:** Maintain a simple sliding window to compute mean over last N episodes. Use O(1) deque-style approach: pop oldest, push newest.

**When to use:** Every episode, update the rolling window array and recalculate mean. Do not use Array.reduce() every time (O(n) cost).

**Example:**
```javascript
class RollingStats {
  constructor(windowSize = 50) {
    this.window = [];
    this.windowSize = windowSize;
  }

  add(value) {
    this.window.push(value);
    if (this.window.length > this.windowSize) {
      this.window.shift(); // Remove oldest
    }
  }

  mean() {
    if (this.window.length === 0) return 0;
    return this.window.reduce((a, b) => a + b, 0) / this.window.length;
  }

  max() {
    return Math.max(...this.window);
  }

  min() {
    return Math.min(...this.window);
  }
}

// Usage
const rewardStats = new RollingStats(50);
rewardStats.add(episodeReward);
const avgReward = rewardStats.mean();
```

### Pattern 4: Viewport Auto-Scroll

**What:** Scroll chart container to show latest data point as new episodes complete.

**When to use:** After each chart update, scroll the container so the most recent episode is visible.

**Example:**
```javascript
function autoScrollChartViewport(chartContainer) {
  // Scroll to right edge to show latest data
  chartContainer.scrollLeft = chartContainer.scrollWidth;
}

// Call after chart.update()
updateChartWithEpisode(episodeNum, reward, rollingAvg);
autoScrollChartViewport(document.getElementById('chartContainer'));
```

### Anti-Patterns to Avoid

- **Recreating the chart every episode:** Causes memory leaks and flicker. Reuse chart object and call `update()`.
- **Using localStorage for unbounded data:** 5MB limit will be exceeded quickly. Use IndexedDB for time-series metrics.
- **Computing rolling average with Array.reduce() every episode:** O(n) cost accumulates. Use deque-style window instead.
- **Storing all raw data in memory:** For long training runs, keep only current episode data in memory; retrieve from IndexedDB for history.
- **Ignoring backpressure on WebSocket:** If chart updates arrive faster than browser can render, implement throttling or batching server-side.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Real-time line chart with animations | Custom canvas renderer | Chart.js | Handling smooth updates, resize responsiveness, legend interactions, and performance optimization is complex |
| Persistent metrics storage | Custom JSON file serialization | IndexedDB with idb wrapper | Raw IndexedDB uses event-based API (verbose); localStorage blocks UI and has 5MB limit; proper error handling and transactions are tricky |
| Rolling average computation | Manual Array operations each episode | Simple class with deque window | Prevents O(n) computation per episode; avoids floating-point accumulation errors |
| CSV/JSON export | Manual string concatenation | Native JSON.stringify + Blob API | String concatenation is error-prone; proper escaping and formatting is tedious |
| Storage quota detection | Guessing when storage is full | navigator.storage.estimate() API | Proactively check quota instead of waiting for QuotaExceededError |

**Key insight:** Charting libraries abstract away complex animation, resizing, and interaction logic that would require significant dev effort to replicate. Storage APIs handle concurrency, durability, and quota management automatically. Time series computation libraries prevent subtle floating-point errors.

## Common Pitfalls

### Pitfall 1: Unbounded Chart Data Causing Memory Leaks

**What goes wrong:** As training runs for many episodes, the chart accumulates data points. The browser's rendering engine must keep all data in memory, causing the page to slow down and eventually crash. This is especially severe with Chart.js if you recreate the chart instead of updating it.

**Why it happens:** Real-time charts typically show all historical data to visualize trends. Without explicit data pruning, the array grows linearly with episode count. Memory usage is O(n) where n = total episodes.

**How to avoid:**
1. Use Chart.js `chart.update()` method (does not leak if chart object is reused).
2. Implement optional data window: keep only last 1000 episodes visible in chart, store full history in IndexedDB.
3. Monitor memory via DevTools; add debug display of chart data array size.

**Warning signs:**
- Page becomes noticeably slower after 5000+ episodes
- Memory usage in DevTools increases every 10 minutes of training
- Chart updates lag (>100ms per update) despite fast WebSocket data

### Pitfall 2: localStorage Quota Exceeded Exception (QuotaExceededError)

**What goes wrong:** Phase context specifies "keep full session history (unbounded episode storage)". localStorage has a 5MB per-origin limit. A typical episode record (reward, steps, epsilon, timestamp as JSON) is ~50 bytes. This allows ~100k episodes before hitting the limit. If not caught, the exception silently fails to save.

**Why it happens:** localStorage is a simple key-value store not designed for large time-series data. No error handling in naive implementations means data loss during training.

**How to avoid:**
1. Use IndexedDB instead of localStorage for metrics (see Storage Limits section).
2. If using localStorage as fallback, always wrap in try-catch for QuotaExceededError.
3. Check quota proactively: `navigator.storage.estimate()` before writing large data batches.
4. Implement graceful degradation: notify user, pause auto-save, or implement LRU eviction.

**Warning signs:**
- Training halts without error message after N episodes (quota hit exactly at limit)
- Page console shows uncaught QuotaExceededError
- Metrics don't persist across page refresh despite "save" button click

### Pitfall 3: WebSocket Backpressure Causing Dropped Metrics

**What goes wrong:** Server broadcasts episode data (reward, steps, epsilon) every episode. If training is very fast (GridWorld episodes complete in microseconds), the server can queue more messages than the browser can render. Browser's incoming message buffer fills, and either the OS TCP buffer overflows (OS drops packets) or the browser drops old messages. Metrics are missing from charts.

**Why it happens:** WebSocket send/receive is fast, but DOM rendering is slower. No flow control means the producer (server) runs unchecked while the consumer (browser) lags.

**How to avoid:**
1. Batch updates server-side: collect 10 episodes, send one update with array.
2. Throttle updates client-side: if chart update takes >50ms, wait before requesting next.
3. Detect backpressure: check `ws.bufferedAmount` on server; if >100 messages queued, pause broadcasts.
4. Use `asyncio.sleep(0)` after broadcasts (see Phase 1 decisions) to yield event loop.

**Warning signs:**
- Chart shows gaps (missing episodes in sequence)
- Fast training (GridWorld) loses data; slow training (Solitaire) doesn't
- Browser console shows "bufferedAmount" warning if you added monitoring

### Pitfall 4: Rolling Average Window Size Mismatch

**What goes wrong:** User-configurable rolling average window (e.g., "mean over last 50 episodes"). If the user changes window size during training, existing rolling averages become invalid. Or if window is too small (e.g., 3 episodes), noise dominates the trend line.

**Why it happens:** Window size is a UI parameter, but chart data is already computed. Changing window mid-training requires recomputing all previous rolling averages from raw data.

**How to avoid:**
1. Lock window size during training (or require restart to apply changes).
2. Store raw episode rewards in memory; recompute rolling average on window change.
3. Set sensible defaults: window size = 50 episodes (reasonable smoothing for typical RL runs).
4. Validate window size: minimum 3, maximum 500.

**Warning signs:**
- Trend line jumps abruptly when user changes window size slider
- Trend line shows high variance (window too small)
- Trend line is flat (window too large, noise filtered out)

### Pitfall 5: Chart Resize/Responsiveness Issues

**What goes wrong:** User resizes browser window. Chart library doesn't automatically resize its canvas/SVG. New episodes are plotted at old dimensions, causing visual distortion.

**Why it happens:** Chart libraries usually require explicit `chart.resize()` or `chart.update()` call on window resize. If not hooked, chart stays at initial dimensions.

**How to avoid:**
1. Add `window.addEventListener('resize', () => chart.resize())` for Chart.js.
2. Use CSS `max-width: 100%` on chart container; let CSS handle responsiveness.
3. Test resize at multiple breakpoints (mobile, tablet, desktop).

**Warning signs:**
- Chart looks squashed after resizing browser
- Chart extends beyond container on mobile
- Data points cluster on one side after resize

## Code Examples

Verified patterns from official sources:

### Real-Time Chart Update (Chart.js)

```javascript
// Source: https://www.chartjs.org/docs/latest/developers/updates.html
const ctx = document.getElementById('rewardChart').getContext('2d');
const chart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Episode Reward',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        tension: 0.1,
        fill: false
      },
      {
        label: 'Rolling Average',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        fill: false,
        tension: 0.1
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Reward' }
      }
    },
    plugins: {
      legend: { display: true }
    }
  }
});

// Update chart every episode
function onEpisodeComplete(episodeNum, reward, rollingAvg) {
  chart.data.labels.push(episodeNum);
  chart.data.datasets[0].data.push(reward);
  chart.data.datasets[1].data.push(rollingAvg);
  chart.update('none'); // 'none' skips animation for responsiveness
}
```

### IndexedDB Storage with Error Handling

```javascript
// Source: https://web.dev/articles/storage-for-the-web
import { openDB } from 'idb';

class MetricsStorage {
  async init() {
    this.db = await openDB('rlMetrics', 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('episodes')) {
          const store = db.createObjectStore('episodes', { keyPath: 'episodeNum' });
          store.createIndex('timestamp', 'timestamp');
        }
      }
    });
  }

  async saveEpisode(episodeNum, reward, steps, epsilon) {
    try {
      const estimate = await navigator.storage.estimate();
      if (estimate.usage > estimate.quota * 0.9) {
        console.warn('Storage quota 90% full');
        // Could implement archival or notify user
      }
      await this.db.add('episodes', {
        episodeNum,
        reward,
        steps,
        epsilon,
        timestamp: Date.now()
      });
    } catch (e) {
      if (e.name === 'QuotaExceededError') {
        console.error('Storage full; unable to save metrics');
        // Fallback: notify user, pause training, or implement LRU
      } else {
        throw e;
      }
    }
  }

  async loadAll() {
    return await this.db.getAll('episodes');
  }

  async clear() {
    await this.db.clear('episodes');
  }
}
```

### Rolling Statistics Calculation

```javascript
class EpisodeStatistics {
  constructor(windowSize = 50) {
    this.rewardWindow = [];
    this.stepsWindow = [];
    this.windowSize = windowSize;
    this.best = { reward: -Infinity, episodeNum: -1 };
  }

  add(episodeNum, reward, steps) {
    // Update windows
    this.rewardWindow.push(reward);
    this.stepsWindow.push(steps);
    if (this.rewardWindow.length > this.windowSize) {
      this.rewardWindow.shift();
      this.stepsWindow.shift();
    }

    // Update best
    if (reward > this.best.reward) {
      this.best = { reward, episodeNum };
    }
  }

  getStats() {
    const n = this.rewardWindow.length;
    if (n === 0) {
      return {
        meanReward: 0,
        meanSteps: 0,
        bestReward: this.best.reward,
        bestEpisode: this.best.episodeNum
      };
    }

    const sumRewards = this.rewardWindow.reduce((a, b) => a + b, 0);
    const sumSteps = this.stepsWindow.reduce((a, b) => a + b, 0);

    return {
      meanReward: sumRewards / n,
      meanSteps: sumSteps / n,
      bestReward: this.best.reward,
      bestEpisode: this.best.episodeNum
    };
  }
}
```

### CSV Export Pattern

```javascript
// Minimal implementation for CSV export
async function exportMetricsAsCSV(storage) {
  const episodes = await storage.loadAll();
  const header = 'Episode,Reward,Steps,Epsilon,Timestamp\n';
  const rows = episodes
    .map(e => `${e.episodeNum},${e.reward},${e.steps},${e.epsilon},${e.timestamp}`)
    .join('\n');

  const csv = header + rows;
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `metrics-${Date.now()}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Redraw entire chart every frame | Incremental updates via `chart.update()` | Chart.js v3+ (2021) | Massive performance improvement; enables 10k+ episodes without lag |
| localStorage for all persistence | IndexedDB for large data, localStorage for settings | HTML5 standard (2014), formalized in recent years | Eliminates storage quota errors; enables true long-form training sessions |
| Manual DOM manipulation for stats | Bind stats to JavaScript objects, update in place | React/Vue adoption (2015+) | Cleaner code, fewer bugs, easier to test |
| Canvas-only charting | SVG + Canvas hybrid rendering (ECharts) | ECharts v5+ (2020) | Trade-off: SVG for interactivity, Canvas for performance |

**Deprecated/outdated:**
- **Smoothie.js:** Streaming charts library (last update 2014). Still works but Chart.js is now standard for real-time metrics.
- **HighCharts (free version):** Older approach to real-time charts; now superseded by ApexCharts and ECharts for open-source use.
- **Plotly.js for real-time:** Designed for static/interactive dashboards, not optimized for high-frequency updates like RL metrics.

## Open Questions

1. **Pause Button Behavior During WebSocket Update**
   - What we know: Phase context specifies "Pause button to freeze chart updates while training continues". Server continues broadcasting episode data via WebSocket while pause is active.
   - What's unclear: Should client discard incoming messages, queue them for later playback, or inform server to stop broadcasts?
   - Recommendation: Simplest approach is to queue messages in client; when unpause is clicked, process the queue. Alternative: send pause signal via WebSocket to server. Keep implementation simple initially.

2. **Export Format Edge Cases**
   - What we know: Phase requires CSV/JSON export capability.
   - What's unclear: Should export include rolling averages computed on browser, or only raw episode data? How to handle special characters in filenames?
   - Recommendation: Export only raw data (episode, reward, steps, epsilon, timestamp). Let users recompute averages in Excel/Python. Use ISO timestamp for reproducibility.

3. **Data Archival Strategy for Unbounded Storage**
   - What we know: Phase specifies "keep full session history (unbounded episode storage)" and use localStorage. IndexedDB research shows this is necessary.
   - What's unclear: How to handle multi-day training runs with 100k+ episodes? IndexedDB quota is browser-dependent and can be revoked.
   - Recommendation: Implement optional "export and clear" workflow: periodically export to CSV/JSON, then clear old episodes from IndexedDB. For localhost-only use, browser quota is typically not a hard limit.

## Sources

### Primary (HIGH confidence)

- **Chart.js Official Documentation** (https://www.chartjs.org/docs/latest/developers/updates.html) - Real-time chart update patterns verified
- **MDN Storage API** (https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria) - localStorage (5-10MB) and IndexedDB quota limits
- **web.dev Storage Guide** (https://web.dev/articles/storage-for-the-web) - IndexedDB recommended for large time-series data; IndexedDB vs localStorage comparison
- **idb Library** (https://www.npmjs.com/package/idb) - Promise-based IndexedDB wrapper; standard practice for IndexedDB usage

### Secondary (MEDIUM confidence)

- **Luzmo JavaScript Chart Libraries Comparison** (https://www.luzmo.com/blog/javascript-chart-libraries) - ECharts and Chart.js confirmed as top real-time chart solutions
- **Embeddable Charting Libraries 2026** (https://embeddable.com/blog/javascript-charting-libraries) - Chart.js, ECharts, and ApexCharts all support real-time updates
- **WebSocket Real-Time Visualization Best Practices** (https://lightningchart.com/blog/data-visualization-websockets/) - Batching and backpressure management for high-frequency WebSocket streams
- **Backpressure in WebSockets** (https://dev.to/safal_bhandari/understanding-backpressure-in-web-socket-471m) - Flow control and buffer management to prevent message loss

### Tertiary (LOW confidence)

- **Smoothie.js** (http://smoothiecharts.org/) - Streaming charts library; legacy but documented for reference (not recommended for new projects)
- **moving-averages npm package** (https://www.npmjs.com/package/moving-averages) - Mentioned as alternative to simple rolling average implementation; plain JS typically sufficient

## Metadata

**Confidence breakdown:**
- **Standard Stack (Chart.js + IndexedDB + idb):** HIGH - Official documentation and extensive adoption confirm these are the industry standard. Chart.js is the most downloaded charting library; IndexedDB is the modern web standard for client-side storage.
- **Architecture Patterns:** HIGH - Chart.js update patterns are documented and battle-tested. IndexedDB transaction patterns are part of the MDN standard.
- **Common Pitfalls:** MEDIUM - WebSocket backpressure and memory leaks are documented in research literature, but specific manifestations depend on implementation details (e.g., episode execution speed, update frequency).
- **Storage Strategy (IndexedDB over localStorage):** HIGH - MDN and web.dev are authoritative sources; localStorage 5MB limit is a hard constraint.

**Research date:** 2026-01-31
**Valid until:** 2026-02-28 (Chart.js and IndexedDB APIs are stable; storage recommendations unlikely to change)

**Note on Chart Library Selection:** Chart.js was selected as the primary recommendation over ECharts and ApexCharts based on:
1. Simplicity: Chart.js has the gentlest learning curve for straightforward line charts.
2. Ecosystem: 2M+ weekly downloads; largest community, most Stack Overflow answers.
3. Sufficient Performance: Chart.js handles 10k episodes without optimization; ECharts handles 10M+ but is overkill for RL metrics.
4. Integration: Pairs naturally with WebSocket updates via incremental `chart.update()` calls.

If future requirements demand 100k+ episodes or advanced interactivity (zooming, drill-down), ECharts is the proven alternative.
