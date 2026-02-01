/**
 * GridWorld RL Training Interface
 * Canvas-based grid renderer with parameter controls and WebSocket communication
 */

// ============================================================================
// WebSocket Client - Real-time training communication
// ============================================================================

class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.handlers = new Map();
        this.reconnectDelay = 3000;
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.updateConnectionStatus(true);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                const handlers = this.handlers.get(data.type) || [];
                handlers.forEach(handler => handler(data.data || data));
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.updateConnectionStatus(false);
            this.reconnect();
        };
    }

    reconnect() {
        console.log(`Reconnecting in ${this.reconnectDelay / 1000}s...`);
        setTimeout(() => this.connect(), this.reconnectDelay);
    }

    on(eventType, callback) {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, []);
        }
        this.handlers.get(eventType).push(callback);
    }

    send(eventType, data = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: eventType, data }));
        } else {
            console.error('WebSocket not connected');
        }
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.textContent = connected ? 'Connected' : 'Disconnected';
            statusEl.className = connected ? 'status-connected' : 'status-disconnected';
        }
    }
}

// ============================================================================
// GridRenderer Class - Canvas-based visualization
// ============================================================================

class GridRenderer {
    constructor(canvasId, gridSize, cellSize = 50) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = gridSize;
        this.cellSize = cellSize;

        // Set canvas dimensions
        this.canvas.width = gridSize * cellSize;
        this.canvas.height = gridSize * cellSize;

        // Initialize state
        this.state = {
            agent_pos: [0, 0],
            goal_pos: [gridSize - 1, gridSize - 1],
            obstacles: [
                [1, 1],
                [2, 2],
                [3, 1]
            ],
            trail: []
        };

        this.maxTrailLength = 20;
    }

    update(newState) {
        // Update agent position and track trail
        if (newState.agent_pos &&
            JSON.stringify(newState.agent_pos) !== JSON.stringify(this.state.agent_pos)) {
            this.state.trail.push([...this.state.agent_pos]);
            // Keep trail bounded to max length
            if (this.state.trail.length > this.maxTrailLength) {
                this.state.trail.shift();
            }
        }

        // Update state
        this.state = { ...this.state, ...newState };
    }

    render() {
        // Clear canvas with background color
        this.ctx.fillStyle = '#f5f5f5';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid lines
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= this.gridSize; i++) {
            const pos = i * this.cellSize;
            // Vertical lines
            this.ctx.beginPath();
            this.ctx.moveTo(pos, 0);
            this.ctx.lineTo(pos, this.canvas.height);
            this.ctx.stroke();
            // Horizontal lines
            this.ctx.beginPath();
            this.ctx.moveTo(0, pos);
            this.ctx.lineTo(this.canvas.width, pos);
            this.ctx.stroke();
        }

        // Draw obstacles (dark filled squares)
        this.ctx.fillStyle = '#333';
        for (const [x, y] of this.state.obstacles) {
            this.ctx.fillRect(
                x * this.cellSize,
                y * this.cellSize,
                this.cellSize,
                this.cellSize
            );
        }

        // Draw trail with fading opacity effect
        for (let i = 0; i < this.state.trail.length; i++) {
            const [x, y] = this.state.trail[i];
            // Opacity increases for more recent positions
            const opacity = (i + 1) / this.state.trail.length * 0.3;
            this.ctx.fillStyle = `rgba(100, 150, 255, ${opacity})`;
            this.ctx.fillRect(
                x * this.cellSize + 5,
                y * this.cellSize + 5,
                this.cellSize - 10,
                this.cellSize - 10
            );
        }

        // Draw goal (green circle)
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

        // Draw agent (red circle)
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
        let frameCount = 0;
        const animate = () => {
            this.render();
            frameCount++;
            if (frameCount % 60 === 0) {  // Log every 60 frames (~1 second)
                console.log('[Renderer] Animation loop running, agent_pos:', this.state.agent_pos);
            }
            requestAnimationFrame(animate);
        };
        animate();
    }
}

// ============================================================================
// MetricsStorage Class - IndexedDB wrapper for episode persistence
// ============================================================================

class MetricsStorage {
    constructor() {
        this.db = null;
        this.dbName = 'rlMetrics';
        this.dbVersion = 1;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);

            request.onsuccess = () => {
                this.db = request.result;
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains('episodes')) {
                    const store = db.createObjectStore('episodes', { keyPath: 'episode' });
                    store.createIndex('timestamp', 'timestamp');
                }
            };
        });
    }

    async saveEpisode(episode, reward, steps, epsilon) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['episodes'], 'readwrite');
            const store = transaction.objectStore('episodes');
            const request = store.put({
                episode,
                reward,
                steps,
                epsilon,
                timestamp: Date.now()
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async loadAll() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['episodes'], 'readonly');
            const store = transaction.objectStore('episodes');
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async clear() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['episodes'], 'readwrite');
            const store = transaction.objectStore('episodes');
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async getCount() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['episodes'], 'readonly');
            const store = transaction.objectStore('episodes');
            const request = store.count();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }
}

// ============================================================================
// EpisodeStatistics Class - Rolling averages for metrics display
// ============================================================================

class EpisodeStatistics {
    constructor(windowSize = 50) {
        this.rewardWindow = [];
        this.stepsWindow = [];
        this.windowSize = windowSize;
        this.best = { reward: -Infinity, episode: -1 };
        this.totalEpisodes = 0;
    }

    add(episode, reward, steps) {
        this.totalEpisodes = episode;

        // Update rolling windows
        this.rewardWindow.push(reward);
        this.stepsWindow.push(steps);
        if (this.rewardWindow.length > this.windowSize) {
            this.rewardWindow.shift();
            this.stepsWindow.shift();
        }

        // Track best episode
        if (reward > this.best.reward) {
            this.best = { reward, episode };
        }
    }

    getMeanReward() {
        if (this.rewardWindow.length === 0) return 0;
        return this.rewardWindow.reduce((a, b) => a + b, 0) / this.rewardWindow.length;
    }

    getMeanSteps() {
        if (this.stepsWindow.length === 0) return 0;
        return this.stepsWindow.reduce((a, b) => a + b, 0) / this.stepsWindow.length;
    }

    getBest() {
        return this.best;
    }

    reset() {
        this.rewardWindow = [];
        this.stepsWindow = [];
        this.best = { reward: -Infinity, episode: -1 };
        this.totalEpisodes = 0;
    }
}

// ============================================================================
// Parameter Management
// ============================================================================

const PARAM_PRESETS = {
    conservative: {
        learning_rate: 0.05,
        epsilon: 1.0,
        discount_factor: 0.99
    },
    balanced: {
        learning_rate: 0.1,
        epsilon: 1.0,
        discount_factor: 0.95
    },
    aggressive: {
        learning_rate: 0.3,
        epsilon: 0.8,
        discount_factor: 0.9
    }
};

function loadParams() {
    // Try to load from localStorage, fallback to defaults
    const learningRate = localStorage.getItem('learning_rate');
    const epsilon = localStorage.getItem('epsilon');
    const discountFactor = localStorage.getItem('discount_factor');

    if (learningRate !== null) {
        document.getElementById('learning-rate').value = learningRate;
        document.getElementById('learning-rate-slider').value = learningRate;
    }
    if (epsilon !== null) {
        document.getElementById('epsilon').value = epsilon;
        document.getElementById('epsilon-slider').value = epsilon;
    }
    if (discountFactor !== null) {
        document.getElementById('discount-factor').value = discountFactor;
        document.getElementById('discount-factor-slider').value = discountFactor;
    }
}

function saveParams() {
    const learningRate = document.getElementById('learning-rate').value;
    const epsilon = document.getElementById('epsilon').value;
    const discountFactor = document.getElementById('discount-factor').value;

    localStorage.setItem('learning_rate', learningRate);
    localStorage.setItem('epsilon', epsilon);
    localStorage.setItem('discount_factor', discountFactor);
}

function applyPreset(presetName) {
    const preset = PARAM_PRESETS[presetName];
    if (!preset) return;

    // Update inputs
    document.getElementById('learning-rate').value = preset.learning_rate;
    document.getElementById('learning-rate-slider').value = preset.learning_rate;
    document.getElementById('epsilon').value = preset.epsilon;
    document.getElementById('epsilon-slider').value = preset.epsilon;
    document.getElementById('discount-factor').value = preset.discount_factor;
    document.getElementById('discount-factor-slider').value = preset.discount_factor;

    // Save to localStorage
    saveParams();
}

function syncInputs(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const input = document.getElementById(inputId);

    slider.addEventListener('input', () => {
        input.value = slider.value;
        saveParams();
    });

    input.addEventListener('input', () => {
        slider.value = input.value;
        saveParams();
    });
}

// ============================================================================
// Training State Management
// ============================================================================

let trainingActive = false;
let wsClient = null;
let metricsStorage = null;
let episodeStats = null;

function updateButtonStates() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const paramInputs = document.querySelectorAll('#learning-rate, #epsilon, #discount-factor, #num-episodes, #learning-rate-slider, #epsilon-slider, #discount-factor-slider');

    if (trainingActive) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        // Lock parameter inputs during training
        paramInputs.forEach(input => input.disabled = true);
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        // Unlock parameter inputs when not training
        paramInputs.forEach(input => input.disabled = false);
    }
}

function showNotification(message, type = 'info') {
    console.log(`[${type}] ${message}`);

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // Add icon based on type
    const icon = document.createElement('span');
    icon.className = 'notification-icon';
    icon.textContent = type === 'error' ? '✗' : type === 'success' ? '✓' : 'ℹ';

    // Add message
    const messageEl = document.createElement('span');
    messageEl.className = 'notification-message';
    messageEl.textContent = message;

    notification.appendChild(icon);
    notification.appendChild(messageEl);

    // Add to container
    const container = document.getElementById('notification-container');
    container.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.classList.add('notification-exit');
        setTimeout(() => {
            container.removeChild(notification);
        }, 300); // Match animation duration
    }, 3000);
}

function startTraining() {
    if (!wsClient) {
        showNotification('WebSocket not connected', 'error');
        return;
    }

    const learningRate = parseFloat(document.getElementById('learning-rate').value);
    const epsilon = parseFloat(document.getElementById('epsilon').value);
    const discountFactor = parseFloat(document.getElementById('discount-factor').value);
    const numEpisodes = parseInt(document.getElementById('num-episodes').value);

    wsClient.send('start_training', {
        learning_rate: learningRate,
        epsilon: epsilon,
        discount_factor: discountFactor,
        num_episodes: numEpisodes
    });

    trainingActive = true;
    updateButtonStates();
}

function stopTraining() {
    if (wsClient) {
        wsClient.send('stop_training');
    }
    trainingActive = false;
    updateButtonStates();
}

function resetTraining() {
    if (wsClient) {
        wsClient.send('reset');
    }
    trainingActive = false;
    updateButtonStates();
    document.getElementById('episode-counter').textContent = '0';
    document.getElementById('step-counter').textContent = '0';
}

function saveQTable() {
    if (wsClient) {
        wsClient.send('save_qtable');
    }
}

function loadQTable() {
    if (wsClient) {
        wsClient.send('load_qtable');
    }
}

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize grid renderer
    const renderer = new GridRenderer('grid-canvas', 5, 50);
    renderer.startAnimationLoop();

    // Make renderer globally accessible for testing
    window.renderer = renderer;

    // Initialize WebSocket client
    wsClient = new WebSocketClient('ws://localhost:8000/ws');
    window.wsClient = wsClient;  // Make globally accessible for debugging

    // Initialize metrics storage (IndexedDB)
    metricsStorage = new MetricsStorage();
    await metricsStorage.init();
    console.log('[Metrics] Storage initialized');

    // Initialize statistics calculator (50-episode rolling window)
    episodeStats = new EpisodeStatistics(50);
    console.log('[Metrics] Statistics calculator initialized');

    // Register WebSocket event handlers
    wsClient.on('training_update', (data) => {
        console.log('[Frontend] Received training_update:', data);

        // Update renderer state
        renderer.update({
            agent_pos: data.agent_pos
        });

        console.log('[Frontend] Renderer state after update:', renderer.state.agent_pos);

        // Update counters
        document.getElementById('episode-counter').textContent = data.episode;
        document.getElementById('step-counter').textContent = data.step;
    });

    wsClient.on('training_complete', (data) => {
        showNotification(`Training complete! ${data.total_episodes} episodes`, 'success');
        trainingActive = false;
        updateButtonStates();
    });

    wsClient.on('training_stopped', (data) => {
        showNotification('Training stopped', 'info');
        trainingActive = false;
        updateButtonStates();
    });

    wsClient.on('reset_complete', (data) => {
        showNotification('Environment reset', 'success');
        renderer.update({
            agent_pos: [0, 0],
            trail: []
        });
        document.getElementById('episode-counter').textContent = '0';
        document.getElementById('step-counter').textContent = '0';
    });

    wsClient.on('save_complete', (data) => {
        if (data.success) {
            showNotification(`Q-table saved to ${data.filepath}`, 'success');
        }
    });

    wsClient.on('load_complete', (data) => {
        if (data.success) {
            showNotification(`Q-table loaded (epsilon: ${data.epsilon.toFixed(3)})`, 'success');
        }
    });

    wsClient.on('error', (data) => {
        showNotification(data.message, 'error');
        trainingActive = false;
        updateButtonStates();
    });

    wsClient.on('episode_complete', async (data) => {
        console.log('[Metrics] Episode complete:', data);

        // Store in IndexedDB
        await metricsStorage.saveEpisode(data.episode, data.reward, data.steps, data.epsilon);

        // Update statistics
        episodeStats.add(data.episode, data.reward, data.steps);

        // Log rolling average (chart integration in Plan 02)
        console.log('[Metrics] Rolling avg reward:', episodeStats.getMeanReward().toFixed(2));
    });

    // Load saved parameters
    loadParams();

    // Set up input synchronization
    syncInputs('learning-rate-slider', 'learning-rate');
    syncInputs('epsilon-slider', 'epsilon');
    syncInputs('discount-factor-slider', 'discount-factor');

    // Set up preset buttons
    document.querySelectorAll('.btn-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = btn.dataset.preset;
            applyPreset(preset);
        });
    });

    // Set up action buttons
    document.getElementById('start-btn').addEventListener('click', startTraining);
    document.getElementById('stop-btn').addEventListener('click', stopTraining);
    document.getElementById('reset-btn').addEventListener('click', resetTraining);
    document.getElementById('save-qtable-btn').addEventListener('click', saveQTable);
    document.getElementById('load-qtable-btn').addEventListener('click', loadQTable);

    // Initialize button states
    updateButtonStates();
});
