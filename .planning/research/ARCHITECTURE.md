# Web-Based RL Training System Architecture

**Domain:** Web-based reinforcement learning training and visualization
**Researched:** 2026-01-30
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Web UI Layer)                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Dashboard  │  │    Controls  │  │ Metrics View │            │
│  │   (Real-time │  │  (Start/Stop │  │ (Rewards,    │            │
│  │    Graphs)   │  │  Parameters) │  │  Episodes)   │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                 │                    │
│         └─────────────────┴─────────────────┘                    │
│                           │                                      │
│                 WebSocket Connection (Bidirectional)             │
│                           │                                      │
├───────────────────────────┴──────────────────────────────────────┤
│                    Web Server (FastAPI)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌─────────────────────────────────────┐    │
│  │ WebSocket      │  │ REST API Endpoints                  │    │
│  │ Manager        │  │ - GET /status                       │    │
│  │ (Connection    │  │ - POST /training/start              │    │
│  │  handling,     │  │ - POST /training/stop               │    │
│  │  broadcasting) │  │ - POST /params (update)             │    │
│  └────────┬───────┘  └────────────────────────────────────┘    │
│           │                                                      │
│           └──────────────────┬─────────────────────────────────┤
│                              │                                  │
├──────────────────────────────┴──────────────────────────────────┤
│         Shared State Layer (Thread-Safe Training State)         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌─────────────────────────────┐     │
│  │ TrainingSession      │  │ MetricsBuffer (Ring Buffer) │     │
│  │ - Current episode    │  │ - Episode rewards           │     │
│  │ - Hyperparameters    │  │ - Step counts               │     │
│  │ - Is running flag    │  │ - Action distribution       │     │
│  │ - Agent reference    │  │ - Real-time streaming       │     │
│  └──────────┬───────────┘  └────────────────┬────────────┘     │
│             │                               │                  │
├─────────────┴───────────────────────────────┴──────────────────┤
│          Training Worker (Background Thread/Process)            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Training Loop    │  │ RL Agent     │  │ Gymnasium        │  │
│  │ (Episode runner) │  │ (Q-learning) │  │ Environment      │  │
│  │ - Reset env      │  │ - Select     │  │ - step()         │  │
│  │ - Run steps      │  │   action     │  │ - reset()        │  │
│  │ - Update Q-table │  │ - Update Q   │  │ - observe state  │  │
│  │ - Emit metrics   │  │ - Decay eps  │  │ - reward logic   │  │
│  └──────────────────┘  └──────────────┘  └──────────────────┘  │
│                                                                  │
│                 (Existing gymnasium-compliant env)              │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Browser UI** | Render dashboard, accept user input, display real-time metrics | React/Vue or Streamlit |
| **WebSocket Manager** | Handle persistent connections, broadcast training metrics to all connected clients | FastAPI WebSockets + asyncio |
| **REST API** | Stateless endpoints for training control and system queries | FastAPI async routes |
| **TrainingSession** | Encapsulate training state (running flag, hyperparams, episode count) | Python class with threading.Lock |
| **MetricsBuffer** | Circular buffer holding recent episodes and metrics for real-time streaming | Collections.deque with max length |
| **Training Loop** | Execute gymnasium step/reset in background, accumulate rewards, update agent | Threading.Thread or asyncio.Task |
| **RL Agent** | Store and update Q-table, select actions (epsilon-greedy), manage learning state | Python class holding numpy Q-table |
| **Gymnasium Env** | Provide game logic, reward function, state transitions | Existing GridWorldEnv (no changes needed) |

## Recommended Project Structure

```
src/
├── gridworld/           # Existing environment (no changes)
│   ├── environment.py   # GridWorldEnv (unchanged)
│   ├── config.py        # GridWorldConfig (unchanged)
│   └── agent.py         # Q-learning agent (stub → implement)
│
├── web/                 # NEW: Web layer
│   ├── __init__.py
│   ├── server.py        # FastAPI app creation and configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py    # REST endpoints (start/stop/status)
│   │   └── websocket.py # WebSocket handler
│   ├── training/
│   │   ├── __init__.py
│   │   ├── session.py   # TrainingSession class (state management)
│   │   ├── worker.py    # Background training loop
│   │   └── metrics.py   # MetricsBuffer for real-time streaming
│   └── frontend/        # NEW: Web UI
│       ├── index.html   # Entry point
│       ├── js/
│       │   ├── app.js   # WebSocket client, UI state
│       │   └── dashboard.js
│       └── css/
│           └── styles.css
│
├── utils/              # Existing utilities (no changes)
│   └── ...
│
└── __init__.py

web_main.py            # Entry point: uvicorn server start
```

### Structure Rationale

- **`src/web/`**: Separates web concerns from RL domain logic. Web layer is entirely new; gymnasuim code unchanged.
- **`src/web/api/`**: REST endpoints and WebSocket in separate modules for clarity.
- **`src/web/training/`**: Training state, worker process, and metrics buffer isolated from API layer.
- **`src/web/frontend/`**: Simple static frontend (HTML/CSS/JS) served by FastAPI. Can scale to SPA framework later if needed.
- **`web_main.py`**: Thin entry point like `play_gridworld_tkinter.py`, starts the FastAPI server.

## Architectural Patterns

### Pattern 1: Separate Web Server from Training Worker

**What:** Training loop runs in a dedicated background thread/process, decoupled from HTTP request handling. Web server is stateless; state lives in shared TrainingSession object.

**When to use:** Long-running workloads that shouldn't block HTTP requests. Critical for real-time web UIs.

**Trade-offs:**
- **Pros:** Responsive HTTP server, no blocking waits, real-time UI updates, easy to pause/resume training
- **Cons:** Thread synchronization needed, requires shared state management with locks, adds complexity

**Example:**
```python
# FastAPI endpoint (runs in HTTP worker process)
@app.post("/training/start")
async def start_training(params: TrainingParams):
    session = get_training_session()
    if session.is_running:
        return {"error": "Already running"}

    session.hyperparams = params
    session.is_running = True

    # Fire off worker thread
    thread = threading.Thread(
        target=training_loop,
        args=(session, env, agent),
        daemon=True
    )
    thread.start()

    return {"status": "started"}

# Training worker (runs in background thread)
def training_loop(session, env, agent):
    while session.is_running:
        obs, _ = env.reset()
        episode_reward = 0

        for step in range(session.max_steps):
            action = agent.select_action(obs)
            obs, reward, terminated, truncated, _ = env.step(action)
            agent.update(obs, action, reward)
            episode_reward += reward

            if terminated or truncated:
                break

        # Thread-safe metric recording
        session.metrics.append({
            "episode": session.episode_count,
            "reward": episode_reward
        })
        session.episode_count += 1
```

### Pattern 2: WebSocket for Real-Time Metrics Streaming

**What:** Persistent WebSocket connection pushes training metrics from server to browser. Avoids polling.

**When to use:** Real-time dashboards, metric streaming, status updates. Standard for modern web UIs.

**Trade-offs:**
- **Pros:** Low latency updates, bandwidth efficient vs polling, simple client code
- **Cons:** Requires WebSocket library support, scaling to many connections requires load balancing

**Example:**
```python
# FastAPI WebSocket endpoint
@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        # Fetch latest metrics from buffer
        new_metrics = get_recent_metrics()

        # Send to browser
        await websocket.send_json({
            "type": "metrics_update",
            "data": new_metrics,
            "timestamp": time.time()
        })

        # Update frequency (not every millisecond)
        await asyncio.sleep(1.0)

# Browser client (JavaScript)
const ws = new WebSocket("ws://localhost:8000/ws/metrics");
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);  // Update React component, Plotly chart, etc.
};
```

### Pattern 3: Metrics Ring Buffer (Circular Buffer)

**What:** Keep last N episodes in memory for real-time streaming. Old data is overwritten.

**When to use:** Avoid unbounded memory growth during long training sessions. Display rolling window of metrics.

**Trade-offs:**
- **Pros:** Fixed memory footprint, efficient for real-time streaming, simple circular semantics
- **Cons:** Can't retrieve old data (add persistent storage later if needed)

**Example:**
```python
from collections import deque

class MetricsBuffer:
    def __init__(self, max_episodes=1000):
        self.buffer = deque(maxlen=max_episodes)
        self.lock = threading.Lock()

    def append(self, metric_dict):
        with self.lock:
            self.buffer.append(metric_dict)

    def get_recent(self, count=50):
        with self.lock:
            return list(self.buffer)[-count:]

    def get_all(self):
        with self.lock:
            return list(self.buffer)
```

### Pattern 4: Conditional State Updates (Avoid Redundant Computation)

**What:** Only start training if not already running. Check flags before executing expensive operations.

**When to use:** Prevent duplicate training sessions, avoid competing parameter updates.

**Trade-offs:**
- **Pros:** Simple to implement, prevents race conditions in single-threaded async code
- **Cons:** Doesn't replace proper locking for complex scenarios; use for simple start/stop

**Example:**
```python
class TrainingSession:
    def __init__(self):
        self.is_running = False
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.is_running:
                return False  # Already running
            self.is_running = True
        return True  # Successfully started

    def stop(self):
        with self.lock:
            self.is_running = False
```

## Data Flow

### Training Session: Start-to-Metrics-to-UI

```
1. Browser User clicks "Start Training"
   ↓
2. JavaScript sends: POST /training/start { learning_rate: 0.1, epsilon: 0.1 }
   ↓
3. FastAPI route receives request (HTTP worker process)
   ↓
4. Validate params; update TrainingSession.hyperparams
   ↓
5. Set TrainingSession.is_running = True
   ↓
6. Spawn background thread running training_loop(session, env, agent)
   ↓
7. Return HTTP 200 immediately (request completes)
   ↓
8. Background thread enters loop:
     - Reset environment
     - Run N steps (agent explores)
     - Compute episode reward
     - Update Q-table
     - Append metrics to MetricsBuffer
     - Check session.is_running flag (continues or exits)
   ↓
9. WebSocket handler reads MetricsBuffer every 1 sec
   ↓
10. WebSocket sends: { type: "metrics", episodes: [...], rewards: [...] }
   ↓
11. Browser receives WebSocket message
   ↓
12. JavaScript updates Plotly chart with new data
   ↓
13. User sees training in real-time
```

### Pause/Resume Flow

```
1. Browser user clicks "Pause"
   ↓
2. POST /training/stop (note: name is misleading; should be "pause")
   ↓
3. FastAPI sets TrainingSession.is_running = False
   ↓
4. HTTP request returns immediately
   ↓
5. Background training loop checks flag on next iteration
   ↓
6. Training thread exits gracefully (no interrupt needed)
   ↓
7. WebSocket sends final metrics
   ↓
8. Browser UI shows "Paused"
   ↓
9. User can resume: POST /training/start again (thread restarts)
```

### Parameter Update During Training

```
1. User adjusts learning_rate slider in UI
   ↓
2. JavaScript sends: POST /params { learning_rate: 0.2 }
   ↓
3. FastAPI updates TrainingSession.hyperparams.learning_rate
   ↓
4. Training loop reads updated value on next episode
   ↓
5. New episodes use new learning rate (no restart needed)
```

## Recommended Integration Strategy

### Phase 1: Web Server + Stateless REST API (Minimal)

**What to build:**
- FastAPI app with basic routes
- `GET /status` - returns current training state
- `POST /training/start` - starts training
- `POST /training/stop` - stops training
- Static HTML page with buttons (no real-time updates yet)

**Why this first:**
- Validates that web layer can control training without breaking gymnasium code
- No WebSocket complexity yet
- Can use HTTP polling for initial prototype

**Effort:** 4-6 hours

---

### Phase 2: WebSocket + Real-Time Metrics

**What to build:**
- WebSocket endpoint for metrics streaming
- MetricsBuffer in TrainingSession
- JavaScript WebSocket client
- Plotly.js chart for real-time reward visualization

**Why next:**
- Enables true real-time experience
- MetricsBuffer prevents unbounded memory growth
- Plotly provides professional-looking learning curves

**Effort:** 6-8 hours

---

### Phase 3: Parameter Controls + Dashboard

**What to build:**
- UI sliders for learning_rate, epsilon, discount_factor
- Real-time parameter updates (no restart needed)
- Episode counter and convergence metrics
- Action distribution histogram

**Why last:**
- Depends on phases 1-2 working
- Allows experimentation with hyperparameters
- Makes learning visible and interactive

**Effort:** 4-5 hours

---

## State Management: How to Avoid Threading Pitfalls

### The Problem
Multiple contexts access shared state:
- **HTTP Worker:** Receives parameter updates from browser
- **Training Thread:** Reads params and updates metrics
- **WebSocket Handler:** Reads metrics for broadcasting

Without proper locking, race conditions occur: metrics are lost, params are partially updated, training crashes.

### The Solution: TrainingSession with Locks

```python
from threading import Lock
from dataclasses import dataclass

@dataclass
class Hyperparameters:
    learning_rate: float = 0.1
    epsilon: float = 0.2
    discount_factor: float = 0.99

class TrainingSession:
    def __init__(self):
        self._lock = Lock()
        self.is_running = False
        self.hyperparams = Hyperparameters()
        self.episode_count = 0
        self.metrics = MetricsBuffer(max_episodes=1000)

    def update_hyperparams(self, learning_rate=None, epsilon=None):
        """Thread-safe parameter update."""
        with self._lock:
            if learning_rate is not None:
                self.hyperparams.learning_rate = learning_rate
            if epsilon is not None:
                self.hyperparams.epsilon = epsilon

    def get_hyperparams(self):
        """Thread-safe read."""
        with self._lock:
            return dataclasses.replace(self.hyperparams)  # Return copy

    def record_episode(self, episode_reward):
        """Thread-safe metric recording."""
        with self._lock:
            self.episode_count += 1
        self.metrics.append({  # MetricsBuffer has its own lock
            "episode": self.episode_count,
            "reward": episode_reward
        })
```

### Key Rules
1. **Always acquire lock before reading/writing shared state**
2. **Keep critical sections brief** (don't call sleep() inside lock)
3. **Use locks consistently** (all accesses to a field use the same lock)
4. **Copy data when returning** (avoid returning references that could be modified)
5. **Prefer immutable objects** (hyperparameters should be frozen)

## Anti-Patterns to Avoid

### Anti-Pattern 1: Blocking the HTTP Server

**What people do:** Training loop runs in FastAPI request handler (synchronous endpoint)
```python
@app.post("/training/start")  # ❌ WRONG
def start_training():
    while True:  # Blocks request indefinitely
        # training code
        pass
    return {"done": True}
```

**Why it's wrong:**
- HTTP request never returns
- Browser hangs
- Can't update params or stop training
- Only one training session possible (server blocked)

**Do this instead:** Spawn thread, return immediately
```python
@app.post("/training/start")  # ✓ RIGHT
async def start_training():
    thread = threading.Thread(target=training_loop, daemon=True)
    thread.start()
    return {"status": "training started"}
```

---

### Anti-Pattern 2: Unbounded Metric Accumulation

**What people do:** Append all metrics to a list
```python
class TrainingSession:
    def __init__(self):
        self.all_metrics = []  # ❌ Grows forever

    def record_episode(self, reward):
        self.all_metrics.append(reward)  # 1M episodes → 1M entries
```

**Why it's wrong:**
- Memory grows without bound during long training sessions
- Metrics broadcast to browser includes gigabytes of old data
- Browser becomes sluggish as chart tries to render millions of points

**Do this instead:** Use bounded ring buffer
```python
self.metrics = MetricsBuffer(max_episodes=1000)  # ✓ RIGHT
# Only latest 1000 episodes in memory
```

---

### Anti-Pattern 3: Direct Mutation of Shared State

**What people do:** Training thread and HTTP handler modify same object
```python
# In HTTP handler
session.hyperparams.learning_rate = 0.2  # ❌ Unprotected write

# In training thread (simultaneously)
rate = session.hyperparams.learning_rate  # ❌ Unprotected read → race condition
```

**Why it's wrong:**
- Training thread might read partial update
- Corruption of dataclass fields
- Unpredictable behavior (works sometimes, crashes other times)

**Do this instead:** Use locks for all shared access
```python
# In HTTP handler
session.update_hyperparams(learning_rate=0.2)  # ✓ Acquires lock internally

# In training thread
rate = session.get_hyperparams().learning_rate  # ✓ Acquires lock, returns copy
```

---

### Anti-Pattern 4: Tight Polling Loop

**What people do:** Browser polls `/status` endpoint every 10ms
```javascript
// ❌ WRONG: Browser hammers server with requests
setInterval(() => {
    fetch("/status").then(r => r.json()).then(updateUI);
}, 10);  // 100 requests per second!
```

**Why it's wrong:**
- Wastes bandwidth and CPU
- Server becomes bottleneck
- Latency increases even with 10ms polling (browser can't receive updates faster)

**Do this instead:** Use WebSocket for push updates
```javascript
// ✓ RIGHT: Server pushes updates when they occur
const ws = new WebSocket("ws://localhost:8000/ws/metrics");
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

---

### Anti-Pattern 5: Training Loop Reads Stale Gym State

**What people do:** Cache environment observation and reuse it
```python
def training_loop():
    obs, _ = env.reset()  # ❌ Only reset once

    while True:
        for episode in range(num_episodes):
            action = agent.select_action(obs)
            obs, reward, terminated, _, _ = env.step(action)

            # ❌ BUG: obs is stale after episode ends
            if terminated:
                obs = agent.current_obs  # Using wrong state!
```

**Why it's wrong:**
- Agent's observation becomes out of sync with gymnasium
- Q-table updates use wrong state transitions
- Learning degrades or crashes

**Do this instead:** Always reset after episode ends
```python
def training_loop():
    while True:
        obs, _ = env.reset()  # ✓ Reset every episode

        while not done:
            action = agent.select_action(obs)
            obs, reward, terminated, truncated, _ = env.step(action)
            agent.update(obs, action, reward)
            done = terminated or truncated
```

---

### Anti-Pattern 6: Synchronous Gymnasium Calls in WebSocket Handler

**What people do:** Compute metrics in WebSocket message handler (blocks socket)
```python
@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket):
    await websocket.accept()

    while True:
        # ❌ WRONG: Blocking call in async handler
        metrics = compute_stats(session.metrics)  # Synchronous!

        await websocket.send_json(metrics)
```

**Why it's wrong:**
- If compute_stats takes 100ms, WebSocket is blocked
- Other connected clients don't receive updates
- Scales poorly with multiple clients

**Do this instead:** Do computation asynchronously or in background
```python
@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket):
    await websocket.accept()

    while True:
        # ✓ RIGHT: Quick read from already-computed buffer
        metrics = session.metrics.get_recent(50)

        await websocket.send_json({
            "type": "metrics",
            "data": metrics
        })
        await asyncio.sleep(1.0)  # 1 Hz update rate
```

## Integration Points with Existing Gymnasium Code

### Point 1: Environment Initialization

**Current code** (unchanged):
```python
env = GridWorldEnv(config=GridWorldConfig(difficulty="medium"))
```

**Web layer integrates by:**
- Creating env once at training start
- Passing env reference to training_loop
- env.reset() and env.step() called only in training thread

**No changes needed to gymnasium code** ✓

---

### Point 2: Agent Implementation

**Current stub** (to be implemented):
```python
class QLearningAgent:
    def __init__(self, env, learning_rate=0.1):
        self.env = env
        self.q_table = np.zeros((env_size, num_actions))

    def select_action(self, obs):
        # Epsilon-greedy
        ...

    def update(self, obs, action, reward, next_obs):
        # Q-learning update
        ...
```

**Web layer integrates by:**
- Creating agent with same interface
- Calling select_action/update from training_loop
- Hyperparams come from session.hyperparams

**Design constraint:** Keep agent as pure learning machine, not coupled to web layer ✓

---

### Point 3: Metrics Emission

**Option A: Agent emits metrics** (tight coupling - avoid)
```python
# ❌ Don't do this: agent shouldn't know about web layer
agent.on_episode_end(reward, episode_num)
```

**Option B: Training loop collects metrics** (loose coupling - recommended)
```python
# ✓ Do this: training loop is the integration point
for episode in range(max_episodes):
    obs, _ = env.reset()
    episode_reward = 0

    for step in range(max_steps):
        action = agent.select_action(obs)
        obs, reward, terminated, _, _ = env.step(action)
        agent.update(obs, action, reward)
        episode_reward += reward
        if terminated:
            break

    # Training loop emits metrics
    session.metrics.append({
        "episode": episode,
        "reward": episode_reward,
        "steps": step
    })
```

## Scalability Considerations

| Scale | Architecture Adjustments | When to Apply |
|-------|--------------------------|---------------|
| 0-1 users (single session) | Single thread, in-process metrics buffer | Now - suitable for localhost learning |
| 1-5 concurrent trainings | Celery task queue, Redis for state persistence | If user wants multiple experiments simultaneously |
| 10+ concurrent trainings | Distributed task workers, database for metrics history | Not needed for personal learning tool |

### Scaling Priorities (in order)

1. **First bottleneck:** WebSocket broadcasts to many browsers become slow
   - **Fix:** Redis pub/sub instead of in-memory metrics buffer
   - **Why:** Each new WebSocket client triggers a new broadcast loop

2. **Second bottleneck:** Training threads consume CPU; can't run multiple experiments
   - **Fix:** Process pool or Celery with worker processes
   - **Why:** Python threads don't run parallel (GIL), so only one training can compute at a time

3. **Third bottleneck:** MetricsBuffer held only in memory, lost on server restart
   - **Fix:** Add persistent storage (SQLite, PostgreSQL) for long-term metric history
   - **Why:** Can't review training history across server restarts

**Recommendation for this project:** Stay at Scale 0 (single session, in-memory). Add distributed components only if blocking issues arise.

## Sources

- [RLInspect: An Interactive Visual Approach to Assess Reinforcement Learning Algorithm](https://arxiv.org/html/2411.08392v1) - Academic framework for RL visualization
- [Top Python Web Development Frameworks in 2026](https://reflex.dev/blog/2026-01-09-top-python-web-frameworks-2026/) - Current Python web framework landscape
- [Real-Time AI Chat: Infrastructure for WebSockets, LLM Streaming, and Session Management](https://render.com/articles/real-time-ai-chat-websockets-infrastructure) - WebSocket architecture patterns
- [WebSocket architecture best practices to design robust realtime system](https://ably.com/topic/websocket-architecture-best-practices) - Real-time system design
- [Building Async Processing Pipelines with FastAPI and Celery](https://devcenter.upsun.com/posts/building-async-processing-pipelines-with-fastapi-and-celery-on-upsun/) - Async worker patterns
- [FastAPI and Streamlit: The Python Duo You Must Know About](https://towardsdatascience.com/fastapi-and-streamlit-the-python-duo-you-must-know-about-72825def1243) - Integration patterns
- [Gymnasium: A Standardized Interface for Reinforcement Learning Environments](https://arxiv.org/pdf/2407.17032) - Official gymnasium architecture
- [Challenges in reinforcement learning algorithms](https://pythonorp.com/challenges-in-reinforcement-learning-algorithms/) - RL implementation pitfalls

---

*Architecture research for: Web-based RL training system integrating with gymnasium environment*
*Researched: 2026-01-30*
