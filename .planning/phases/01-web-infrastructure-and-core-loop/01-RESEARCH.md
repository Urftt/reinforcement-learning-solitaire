# Phase 1: Web Infrastructure & Core Loop - Research

**Researched:** 2026-01-30
**Domain:** Web-based real-time training interface with Python backend and async WebSocket communication
**Confidence:** HIGH

## Summary

Phase 1 requires building a web interface where users can train a Q-learning agent on GridWorld with real-time visualization and parameter control. The research identifies a standard, proven stack combining FastAPI (async Python framework with native WebSocket support), vanilla JavaScript (for simplicity on localhost), and Canvas-based grid visualization.

The existing GridWorld environment (Gymnasium-compliant) and infrastructure are mature and ready to integrate. The key architectural decisions revolve around:
- Using FastAPI with Starlette's WebSocket support for real-time bidirectional communication
- Running the training loop in a background asyncio task to avoid blocking the event loop
- Using a ConnectionManager pattern to maintain WebSocket state between frontend and backend
- Streaming game state updates as JSON messages following event-based conventions

The main pitfalls to avoid are: (1) blocking the asyncio event loop with synchronous training code, (2) losing WebSocket connections due to missing heartbeat/ping-pong mechanisms, and (3) updating grid visualization too frequently (causing DOM thrashing). Standards exist for all three problems.

**Primary recommendation:** Use FastAPI with WebSocket + vanilla JavaScript Canvas for grid visualization + asyncio.create_task() for non-blocking training loop. This stack is production-grade, has zero external dependencies beyond what's already in the project, and is the de facto standard for this use case.

## Standard Stack

The established libraries/tools for building real-time RL training interfaces:

### Core Framework
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.104.1+ | ASGI async web framework with native WebSocket support | Industry-standard for async Python APIs; minimal overhead; native WebSocket handling with Starlette |
| Starlette | Built into FastAPI | WebSocket protocol handling and ASGI implementation | FastAPI re-exports Starlette's WebSocket, battle-tested in production systems |
| Pydantic | 2.x | Request/response validation and serialization | FastAPI dependency; validates WebSocket message payloads |
| Uvicorn | 0.24.0+ | ASGI server for running FastAPI locally | Standard production-ready localhost server |

### Environment & Training
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Gymnasium | 1.2.3+ | Standard RL environment interface | Maintained fork of OpenAI Gym; GridWorld already implements this |
| NumPy | 1.24.0+ | Numerical operations for Q-table and state handling | Already in project dependencies; required by Gymnasium |

### Frontend Technologies
| Technology | Purpose | When to Use |
|-----------|---------|-------------|
| Vanilla JavaScript (ES6+) | WebSocket client, grid rendering, form handling | Localhost-only app with simple UI; no build step required |
| Canvas API | Real-time grid visualization (agent position, obstacles, goal) | Small grids (5x7) with frequent updates; ~60fps capable |
| JSON message format | WebSocket communication protocol | Standard, human-readable, native JavaScript support |

### Supporting Libraries (Optional but Recommended)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | 0.0.6+ | Form data parsing in FastAPI | Only if adding file upload features (deferred) |
| aiofiles | 23.0.0+ | Async file I/O (if saving/loading Q-tables) | Feature 1.5 (deferred) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| FastAPI | Flask + Flask-SocketIO | Flask requires threading; less async-native; more boilerplate for WebSocket |
| FastAPI | Django Channels | Heavier framework; overkill for localhost learning tool; more complex setup |
| FastAPI | Tornado | Older pattern; less type-hinting support; smaller ecosystem |
| Vanilla JavaScript | React | Adds build step and complexity; overkill for simple localhost grid; increases bundle size |
| Vanilla JavaScript | Vue.js | Same as React; unnecessary coupling for this use case |
| Canvas | SVG | SVG degrades at 10,000+ elements; Canvas is 10-20x faster for frequent updates; Canvas needed for 60fps grid updates |
| Canvas | WebGL | Overkill for simple 2D grid; adds API complexity |
| WebSocket | HTTP polling/long-polling | Higher latency, higher server load; WebSocket is bidirectional standard |
| WebSocket | Server-Sent Events (SSE) | SSE is unidirectional (server→client only); need bidirectional for training controls |

**Installation:**
```bash
# Backend dependencies (FastAPI + Uvicorn already compatible with pyproject.toml)
pip install "fastapi>=0.104.1" "uvicorn[standard]>=0.24.0" "starlette>=0.27.0"

# Already in project
pip install "gymnasium>=0.29.0" "numpy>=1.24.0"

# Frontend: No installation needed (vanilla JavaScript, Canvas API is native)
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── gridworld/
│   ├── environment.py        # Existing: Gymnasium GridWorld implementation
│   ├── agent.py              # Existing: Q-learning agent (to be completed)
│   ├── config.py             # Existing: GridWorldConfig, QLearningConfig
│   ├── train.py              # Existing: Training loop (to be refactored)
│   └── server.py             # NEW: FastAPI application, WebSocket endpoints
├── visualization/            # Existing but underutilized
│   ├── __init__.py
│   └── (HTML/JS frontend served as static files)
└── main.py                   # Entry point

static/
├── index.html                # NEW: Main page, Canvas grid, controls
├── app.js                     # NEW: WebSocket client, grid renderer
├── styles.css                # NEW: Clean minimal styling
└── favicon.ico               # Optional

```

### Pattern 1: FastAPI WebSocket with ConnectionManager

**What:** Centralized WebSocket connection management to handle multiple concurrent clients (future-proofing) and structured message passing.

**When to use:** For any web application that needs bidirectional, real-time communication with multiple clients connected simultaneously.

**Example:**
```python
# src/gridworld/server.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import json
import asyncio

class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Client disconnected; will be cleaned up on next receive attempt
                pass

manager = ConnectionManager()
app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming command (start, stop, param change)
            await process_command(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

**Source:** [FastAPI WebSocket Documentation](https://fastapi.tiangolo.com/advanced/websockets/)

### Pattern 2: Non-Blocking Training Loop with asyncio.create_task()

**What:** Running a long-running training loop in the background without blocking the event loop, allowing WebSocket messages to be received and processed concurrently.

**When to use:** Any scenario where the backend must respond to client requests while performing heavy computation in the background.

**Example:**
```python
# Training loop that doesn't block event loop
training_task = None
training_state = {"running": False, "episode": 0, "step": 0}

async def training_loop(config):
    """Run training in a non-blocking way."""
    env = GridWorldEnv(config["env"])
    agent = QLearningAgent(config["agent"])

    training_state["running"] = True
    for episode in range(config["agent"]["num_episodes"]):
        obs, _ = env.reset()
        done = False
        step = 0

        while not done and step < config["env"]["max_steps"]:
            action = agent.select_action(obs)
            obs, reward, terminated, truncated, _ = env.step(action)
            agent.update(obs, action, reward)

            training_state["episode"] = episode
            training_state["step"] = step

            # Broadcast state to all connected clients every N steps
            if step % 10 == 0:
                await manager.broadcast({
                    "type": "training_update",
                    "episode": episode,
                    "step": step,
                    "agent_pos": obs.tolist()
                })

            done = terminated or truncated
            step += 1

        # Small yield to allow event loop to process other tasks
        await asyncio.sleep(0)

    training_state["running"] = False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global training_task
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            command = data.get("type")

            if command == "start_training":
                if training_task is None or training_task.done():
                    training_task = asyncio.create_task(
                        training_loop(data.get("config", {}))
                    )

            elif command == "stop_training":
                if training_task and not training_task.done():
                    training_task.cancel()
                training_state["running"] = False

            elif command == "reset":
                if training_task and not training_task.done():
                    training_task.cancel()
                training_state = {"running": False, "episode": 0, "step": 0}

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Source:** [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html), [FastAPI Concurrency](https://fastapi.tiangolo.com/async/)

### Pattern 3: JSON Event-Based WebSocket Messages

**What:** Structured message format using [type, data] array convention for clear separation of event type and payload.

**When to use:** Any bidirectional WebSocket communication to maintain consistency with standard conventions and enable extensibility.

**Example:**
```javascript
// Client sends: ["start_training", { "learning_rate": 0.1, "epsilon": 1.0 }]
// Server responds: ["training_update", { "episode": 5, "step": 120, "agent_pos": [2, 3] }]
// Client sends: ["stop_training", {}]
// Server responds: ["training_stopped", { "final_episode": 50 }]

// src/gridworld/server.py - Message handler
async def process_command(message: dict):
    """Process incoming WebSocket command."""
    msg_type = message.get("type")
    payload = message.get("data", {})

    if msg_type == "start_training":
        config = payload  # Contains learning_rate, epsilon, etc.
        # ... start training

    elif msg_type == "update_params":
        # Update training parameters before next run
        agent_config.learning_rate = payload.get("learning_rate")
        agent_config.epsilon = payload.get("epsilon")

    elif msg_type == "reset":
        # Reset environment to initial state
        # ...
```

**Source:** [JSON Event Convention for WebSockets](https://thoughtbot.com/blog/json-event-based-convention-websockets)

### Pattern 4: Canvas Grid Visualization with RequestAnimationFrame

**What:** Efficient DOM-less rendering using HTML5 Canvas with requestAnimationFrame() to sync redraws with browser's refresh rate.

**When to use:** Real-time visualization of frequently-changing grid state (agent position, trail effect); avoids DOM thrashing.

**Example:**
```javascript
// static/app.js
class GridRenderer {
    constructor(canvasId, gridSize, cellSize = 40) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = gridSize;
        this.cellSize = cellSize;

        this.canvas.width = gridSize * cellSize;
        this.canvas.height = gridSize * cellSize;

        this.state = {
            agent_pos: null,
            goal_pos: null,
            obstacles: [],
            trail: [] // Recent positions for fading trail effect
        };
    }

    update(newState) {
        // Update internal state from WebSocket message
        this.state = { ...this.state, ...newState };
        // Don't render here; render in animation loop
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#f0f0f0';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid lines
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

        // Draw obstacles
        this.ctx.fillStyle = '#333';
        for (const [x, y] of this.state.obstacles) {
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        }

        // Draw trail with fading effect
        for (let i = 0; i < this.state.trail.length; i++) {
            const [x, y] = this.state.trail[i];
            const opacity = (i + 1) / this.state.trail.length * 0.3;
            this.ctx.fillStyle = `rgba(100, 150, 255, ${opacity})`;
            this.ctx.fillRect(x * this.cellSize + 5, y * this.cellSize + 5, this.cellSize - 10, this.cellSize - 10);
        }

        // Draw goal
        this.ctx.fillStyle = '#4caf50';
        const [gx, gy] = this.state.goal_pos;
        this.ctx.beginPath();
        this.ctx.arc((gx + 0.5) * this.cellSize, (gy + 0.5) * this.cellSize, this.cellSize / 3, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw agent
        if (this.state.agent_pos) {
            const [ax, ay] = this.state.agent_pos;
            this.ctx.fillStyle = '#ff6b6b';
            this.ctx.beginPath();
            this.ctx.arc((ax + 0.5) * this.cellSize, (ay + 0.5) * this.cellSize, this.cellSize / 2.5, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
}

// Animation loop synced with screen refresh rate
const renderer = new GridRenderer('grid-canvas', 5);

function animationLoop() {
    renderer.render();
    requestAnimationFrame(animationLoop);
}

animationLoop();

// WebSocket receives state updates
ws.addEventListener('message', (event) => {
    const [type, data] = JSON.parse(event.data);
    if (type === 'training_update') {
        renderer.update(data);
    }
});
```

**Source:** [Canvas Performance Best Practices](https://blog.ag-grid.com/optimising-html5-canvas-rendering-best-practices-and-techniques/), [SVG vs Canvas 2025](https://www.svggenie.com/blog/svg-vs-canvas-vs-webgl-performance-2025)

### Anti-Patterns to Avoid

- **Block the asyncio event loop with synchronous training:** If you use `env.step()` in a synchronous blocking way without `await asyncio.sleep(0)`, the event loop cannot process WebSocket messages. Solution: Use `asyncio.create_task()` and yield control with `await asyncio.sleep(0)`.

- **Update DOM elements directly for grid rendering:** Manipulating the DOM frequently (adding/removing divs, changing innerHTML) causes reflows/repaints that tank performance. Solution: Use Canvas API instead.

- **Send WebSocket messages on every single step:** Sending a message for every training step (could be thousands per episode) floods the network and browser. Solution: Batch updates, send every N steps (e.g., every 10 steps).

- **No heartbeat mechanism for WebSocket connections:** Connections drop silently without a ping/pong mechanism. Solution: Implement periodic heartbeat or rely on FastAPI/Starlette's built-in connection validation.

- **Synchronous training code blocking HTTP requests:** Even though this phase only has WebSocket, async APIs like `run_in_threadpool()` may be needed if training code is CPU-bound. Solution: Use `fastapi.concurrency.run_in_threadpool()` for sync code.

## Don't Hand-Roll

Problems that look simple but have existing, proven solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| WebSocket protocol handling | Custom TCP socket code | Starlette/FastAPI WebSocket | Handles connection lifecycle, message framing, heartbeat, error codes, handshake |
| Real-time grid visualization | DOM manipulation (appendChild loops) | Canvas API | DOM updates cause reflow/repaint overhead; Canvas is 10-20x faster for frequent updates; scales to 60fps |
| Training loop without blocking | Manual threading with locks | asyncio.create_task() + await | asyncio is built for this; threading adds complexity and race conditions |
| Parameter serialization | Manual JSON string building | Pydantic models | Automatic validation, type hints, error messages |
| Form data handling | Manual query string parsing | FastAPI dependencies + Pydantic | Built-in validation, type coercion, error responses |
| Static file serving | Manual file open/read in routes | FastAPI StaticFiles + Starlette | Handles MIME types, caching headers, directory traversal protection |

**Key insight:** The three hardest problems in this phase (WebSocket, grid rendering, non-blocking training) all have mature, industry-standard solutions. Building custom implementations introduces bugs, performance issues, and maintenance burden. The tools are mature, free, and already in the Python ecosystem.

## Common Pitfalls

### Pitfall 1: Blocking the asyncio Event Loop with Synchronous Training Code

**What goes wrong:** If the training loop calls `env.step()` continuously without yielding control back to the event loop, the event loop cannot process WebSocket messages. The frontend appears frozen or unresponsive to user clicks.

**Why it happens:** Python's asyncio is cooperative multitasking—tasks must explicitly yield control with `await`. A tight loop doing CPU-bound work (computing Q-table updates) will hold the event loop until the loop finishes.

**How to avoid:**
- Use `asyncio.create_task()` to run training in a separate task
- Insert `await asyncio.sleep(0)` periodically in the training loop to yield control
- Alternatively, use `fastapi.concurrency.run_in_threadpool()` if training code is unavoidably synchronous

**Warning signs:**
- WebSocket messages not being received while training runs
- Frontend UI becomes unresponsive after clicking "Start Training"
- Browser shows loading spinner that never completes

**Verification:**
```python
# GOOD: Yields control to event loop
async def training_loop():
    for episode in range(100):
        # ... training code ...
        await asyncio.sleep(0)  # Yield control

# BAD: Blocks event loop
async def training_loop():
    for episode in range(100):
        # ... training code ...
        # No await = event loop blocked!
```

### Pitfall 2: WebSocket Connections Silently Dropping

**What goes wrong:** A WebSocket connection works initially but drops after 30-60 seconds of inactivity, and the frontend doesn't reconnect automatically. User thinks training stopped when it's actually still running.

**Why it happens:** Proxies, load balancers, or firewalls close idle connections. Without a heartbeat mechanism (ping/pong), both sides believe the connection is still alive.

**How to avoid:**
- FastAPI/Starlette automatically handle ping/pong if the client initiates it
- Implement client-side heartbeat: send a ping message every 30 seconds
- Or: Rely on connection timeouts being long (most setups are fine by default)

**Warning signs:**
- Training runs fine for 30-60 seconds, then frontend stops receiving updates
- Console shows WebSocket connection closed with code 1006 (abnormal closure)
- Reloading the page restores connection

**Verification:**
```javascript
// Client-side heartbeat (optional but safe)
setInterval(() => {
    ws.send(JSON.stringify(["ping", {}]));
}, 30000); // Every 30 seconds
```

### Pitfall 3: Canvas Rendering Performance Degradation

**What goes wrong:** Grid updates slow down over time, causing frame rate to drop from 60fps to 10fps despite sending the same volume of messages.

**Why it happens:** Two common causes: (1) Trail effect accumulates unbounded, storing thousands of old positions; (2) Canvas context leaks memory if you don't clear it properly between frames.

**How to avoid:**
- Keep trail array bounded (max ~20 recent positions)
- Always clear canvas at the start of each render: `ctx.clearRect(0, 0, width, height)` or fill with background color
- Profile with Chrome DevTools Performance tab to detect memory leaks

**Warning signs:**
- Frame rate monitor shows gradual decline (60fps → 30fps → 10fps)
- DevTools Memory tab shows heap size growing unbounded
- GPU memory usage increasing

**Verification:**
```javascript
render() {
    // GOOD: Limit trail to recent positions
    if (this.state.trail.length > 20) {
        this.state.trail.shift(); // Remove oldest
    }

    // GOOD: Clear canvas properly
    this.ctx.fillStyle = '#f0f0f0';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
}
```

### Pitfall 4: Sending Too Many WebSocket Messages

**What goes wrong:** If you send a WebSocket message for every single training step, you can send 1000+ messages per second on a fast training loop. This floods the network and browser, causing lag.

**Why it happens:** Developers often think "send state every step" without considering the volume. With max_steps=100 per episode and 500 episodes, that's 50,000 messages in one training run.

**How to avoid:**
- Batch updates: send every N steps (e.g., every 10 steps)
- Use the `step % UPDATE_INTERVAL == 0` pattern
- Consider update frequency relative to human perception (humans can't see >60fps anyway)

**Warning signs:**
- Network tab shows 10,000+ WebSocket messages in one training run
- Browser DevTools shows high CPU usage from message processing
- Training loop timing shows most time spent on WebSocket sends, not training

**Verification:**
```python
# GOOD: Batch updates
UPDATE_INTERVAL = 10

for step in range(max_steps):
    obs, reward, done, _, _ = env.step(action)
    agent.update(obs, action, reward)

    if step % UPDATE_INTERVAL == 0:  # Send every 10 steps
        await manager.broadcast({
            "type": "training_update",
            "step": step,
            "agent_pos": obs.tolist()
        })
```

### Pitfall 5: Parameter Changes During Training Don't Take Effect

**What goes wrong:** User adjusts learning rate in the UI during training, but the agent continues using the old learning rate. The change only takes effect on the next training run.

**Why it happens:** The training loop reads `agent_config.learning_rate` once at the start. Subsequent changes to the config object don't affect the running agent unless it explicitly re-reads the config.

**How to avoid:**
- Document clearly: "Parameters lock during training; stop training to change parameters"
- Alternatively: have training code re-read config at the start of each episode
- Or: require explicit "Apply" button that stops and restarts training

**Warning signs:**
- User adjusts learning rate slider, expects immediate effect, doesn't see it
- Training metrics don't show any change in behavior after parameter change

**Verification:** This is a UX decision covered by the CONTEXT.md decision: "Parameters can only be changed before training starts - locked during training."

## Code Examples

Verified patterns from official sources and industry standards:

### FastAPI WebSocket Connection Manager

```python
# Source: FastAPI official documentation
# src/gridworld/server.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                pass

manager = ConnectionManager()
app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await process_training_command(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### JavaScript WebSocket Client with Event Dispatcher

```javascript
// Source: JSON event convention + WebSocket standard
// static/app.js

class WebSocketClient {
    constructor(url) {
        this.ws = new WebSocket(url);
        this.handlers = {};

        this.ws.addEventListener('open', () => {
            console.log('Connected to training server');
        });

        this.ws.addEventListener('message', (event) => {
            const [type, data] = JSON.parse(event.data);
            if (this.handlers[type]) {
                this.handlers[type].forEach(callback => callback(data));
            }
        });

        this.ws.addEventListener('close', () => {
            console.warn('Connection closed. Attempting to reconnect...');
            setTimeout(() => this.reconnect(), 3000);
        });
    }

    on(eventType, callback) {
        if (!this.handlers[eventType]) {
            this.handlers[eventType] = [];
        }
        this.handlers[eventType].push(callback);
    }

    send(eventType, data = {}) {
        this.ws.send(JSON.stringify([eventType, data]));
    }

    reconnect() {
        this.ws = new WebSocket('ws://localhost:8000/ws');
    }
}

const ws = new WebSocketClient('ws://localhost:8000/ws');

ws.on('training_update', (data) => {
    renderer.update(data);
});

ws.on('training_stopped', (data) => {
    console.log('Training stopped at episode', data.final_episode);
});
```

### Non-Blocking Training Loop with asyncio

```python
# Source: Python asyncio best practices
# src/gridworld/server.py

training_task = None

async def training_loop(env_config: dict, agent_config: dict, num_episodes: int):
    """Run training without blocking the event loop."""
    from src.gridworld.environment import GridWorldEnv
    from src.gridworld.agent import QLearningAgent

    env = GridWorldEnv(env_config)
    agent = QLearningAgent(agent_config)

    for episode in range(num_episodes):
        obs, _ = env.reset()
        done = False
        step = 0

        while not done:
            action = agent.select_action(obs)
            obs, reward, terminated, truncated, _ = env.step(action)
            agent.update(obs, action, reward)

            if step % 10 == 0:  # Batch updates
                await manager.broadcast({
                    "type": "training_update",
                    "episode": episode,
                    "step": step,
                    "agent_pos": obs.tolist()
                })

            done = terminated or truncated
            step += 1

        # Yield control to event loop every episode
        await asyncio.sleep(0)

    await manager.broadcast({
        "type": "training_complete",
        "final_episode": num_episodes
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global training_task
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            payload = data.get("data", {})

            if msg_type == "start_training":
                if training_task is None or training_task.done():
                    training_task = asyncio.create_task(
                        training_loop(
                            payload.get("env_config", {}),
                            payload.get("agent_config", {}),
                            payload.get("num_episodes", 500)
                        )
                    )

            elif msg_type == "stop_training":
                if training_task and not training_task.done():
                    training_task.cancel()
                    await manager.broadcast({
                        "type": "training_stopped",
                        "final_episode": payload.get("episode", 0)
                    })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if training_task and not training_task.done():
            training_task.cancel()
```

### Canvas Grid Renderer with Animation Loop

```javascript
// Source: Canvas API best practices + requestAnimationFrame standard
// static/app.js

class GridRenderer {
    constructor(canvasId, gridSize, cellSize = 40) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = gridSize;
        this.cellSize = cellSize;

        this.canvas.width = gridSize * cellSize;
        this.canvas.height = gridSize * cellSize;

        this.state = {
            agent_pos: [0, 0],
            goal_pos: [gridSize - 1, gridSize - 1],
            obstacles: [],
            trail: []
        };

        this.startAnimationLoop();
    }

    update(newState) {
        // Track agent trail (max 20 positions)
        if (newState.agent_pos && newState.agent_pos !== this.state.agent_pos) {
            this.state.trail.push(newState.agent_pos);
            if (this.state.trail.length > 20) {
                this.state.trail.shift();
            }
        }
        this.state = { ...this.state, ...newState };
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = '#f0f0f0';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

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

        // Obstacles
        this.ctx.fillStyle = '#333';
        for (const [x, y] of this.state.obstacles) {
            this.ctx.fillRect(x * this.cellSize, y * this.cellSize, this.cellSize, this.cellSize);
        }

        // Trail (fading effect)
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
        this.ctx.fillStyle = '#4caf50';
        const [gx, gy] = this.state.goal_pos;
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

    startAnimationLoop() {
        const animate = () => {
            this.render();
            requestAnimationFrame(animate);
        };
        animate();
    }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tkinter for desktop UI | Browser-based web UI | 2010s-2020s | Web UIs are more accessible, easier to style, support real-time websockets natively |
| OpenAI Gym | Gymnasium (maintained fork) | 2023 | Gym is no longer maintained; Gymnasium is the de facto standard |
| Custom RL training code | Gymnasium + agent interface | 2023+ | Standardized interface enables ecosystem of compatible tools and algorithms |
| HTTP polling for updates | WebSocket bidirectional | 2010s+ | WebSocket eliminates latency and bandwidth overhead; now industry standard |
| DOM manipulation for rendering | Canvas API for real-time graphics | 2010s+ | Canvas 10-20x faster for frequent updates; standard for interactive visualizations |
| Flask for async | FastAPI for async Python | 2018+ | FastAPI built on ASGI; async-first design; significantly faster and more natural |

**Deprecated/outdated:**
- Tkinter: Dated UI toolkit; works but feels clunky; no real-time visualization support
- Flask (without async): Synchronous by default; requires threading for WebSocket; more boilerplate
- jQuery event handling: Replaced by modern JavaScript (ES6 modules, async/await); still works but unnecessary bloat
- SVG for dynamic grid visualization: Slower than Canvas for frequent updates; fine for static diagrams

## Open Questions

1. **Q-Learning Agent Implementation**
   - What we know: Config defines learning_rate, discount_factor, epsilon, epsilon_decay (in config.py); agent.py stub exists
   - What's unclear: Exact epsilon-greedy implementation details for this specific GridWorld; whether to store Q-table in memory or on disk; how to track/serialize learning progress across sessions
   - Recommendation: Implement epsilon-greedy in agent.py following standard Q-learning algorithm. For Phase 1, keep Q-table in memory. Feature 1.5 (save/load) can add persistence. Verify implementation matches CONTEXT.md requirement QL-01 through QL-05.

2. **Update Frequency for UI**
   - What we know: CONTEXT.md specifies "Every N steps (configurable by user), Default interval: Every 10 steps"
   - What's unclear: Whether N is configurable in UI or only backend code; whether this means canvas rerenders or WebSocket message sends (different concepts)
   - Recommendation: For Phase 1 MVP, hardcode N=10. Canvas animation loop (requestAnimationFrame) runs independent of update frequency. WebSocket messages sent every 10 steps. In later phase, add UI slider for this setting if desired.

3. **Difficulty Levels Preset Parameters**
   - What we know: PROJECT.md mentions "Multiple difficulty levels (easy, medium, hard presets)" are already implemented in GridWorld
   - What's unclear: Whether Phase 1 should expose difficulty selection in UI or if it's just backend infrastructure; how difficulty translates to env_config parameters
   - Recommendation: Check existing GridWorld config.py for difficulty presets. Expose in UI as radio buttons or dropdown in "easy/medium/hard" form. Map each to predefined obstacle counts and grid sizes.

4. **Error Handling and Recovery**
   - What we know: WebSocket can disconnect; training can crash; parameters can be invalid
   - What's unclear: UI/UX for communicating errors back to frontend; whether validation happens client-side, server-side, or both
   - Recommendation: Add error type in message protocol: ["error", { "code": "invalid_param", "message": "Learning rate must be between 0 and 1" }]. Client displays toasts/alerts. Server validates all inputs with Pydantic before training starts.

5. **Q-Table Visualization**
   - What we know: CONTEXT.md VIZ requirements specify agent position visualization and learning progress (episode/step count)
   - What's unclear: Whether Phase 1 includes Q-value heatmap visualization or just agent position; VIZ-01 says "position update" but doesn't mention Q-table heatmap (likely Phase 2)
   - Recommendation: For Phase 1, focus on agent position + trail effect (specified in CONTEXT decisions). Defer Q-value heatmap visualization to Phase 2 per CONTEXT deferred ideas (no heatmaps mentioned there, so they can come later).

## Sources

### Primary (HIGH confidence)

- **FastAPI WebSocket Documentation** - https://fastapi.tiangolo.com/advanced/websockets/
  - Official pattern for WebSocket endpoints, ConnectionManager, message handling

- **Gymnasium Documentation** - https://gymnasium.farama.org/index.html
  - Standard RL environment interface; version 1.2.3+ supports Python 3.10

- **Python asyncio Documentation** - https://docs.python.org/3/library/asyncio.html
  - asyncio.create_task(), asyncio.sleep() patterns for non-blocking operations

- **Canvas API Performance Guide** - https://blog.ag-grid.com/optimising-html5-canvas-rendering-best-practices-and-techniques/
  - Canvas 10-20x faster than SVG for frequent updates; animation loop patterns

- **FastAPI Background Tasks & Concurrency** - https://fastapi.tiangolo.com/async/ and https://fastapi.tiangolo.com/tutorial/background-tasks/
  - Blocking vs non-blocking patterns; event loop management

### Secondary (MEDIUM confidence)

- [WebSocket Architecture Best Practices](https://ably.com/topic/websocket-architecture-best-practices) - Connection reliability, scaling patterns

- [JSON Event-Based Convention for WebSockets](https://thoughtbot.com/blog/json-event-based-convention-websockets) - Message structure convention; widely adopted in industry

- [FastAPI Static Files](https://fastapi.tiangolo.com/tutorial/static-files/) - Serving HTML/CSS/JS from FastAPI

- [SVG vs Canvas Performance 2025](https://www.svggenie.com/blog/svg-vs-canvas-vs-webgl-performance-2025) - Grid rendering technology comparison

- [Python Real-Time Communication Patterns](https://ably.com/topic/websockets-python) - Multiple concurrent connections, scaling considerations

### Tertiary (LOW confidence - WebSearch verification only)

- Various Medium blog posts on FastAPI WebSocket patterns (verified against official docs)
- Stack Overflow discussions on asyncio blocking patterns (verified against official documentation)

## Metadata

**Confidence breakdown:**
- **Standard Stack:** HIGH - FastAPI, Gymnasium, Canvas are industry standards; versions verified
- **Architecture Patterns:** HIGH - FastAPI WebSocket, asyncio.create_task(), JSON event convention all verified with official sources
- **Code Examples:** HIGH - All examples cross-referenced with official documentation
- **Common Pitfalls:** HIGH - Based on documented patterns and common failure modes from official sources
- **Q-Learning specifics:** MEDIUM - Config templates exist; implementation details need Phase 1 planning task

**Research date:** 2026-01-30
**Valid until:** 2026-02-15 (FastAPI/Gymnasium are stable; 30-day validity for standard tech)

**Applicability:**
- This research is specific to localhost-only learning tool (not production scaling)
- GridWorld environment is small (5-7x5-7 grids); all stack choices are appropriate
- Team is Python-focused; browser-based interface is preferred over desktop (Tkinter)
- Real-time visualization is a hard requirement, not optional

---

*Research completed for Phase 1: Web Infrastructure & Core Loop*
*Constraint-driven by CONTEXT.md decisions*
*Ready for gsd-planner to create implementation tasks*
