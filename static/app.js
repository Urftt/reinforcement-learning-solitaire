/**
 * GridWorld RL Training Interface
 * Canvas-based grid renderer with parameter controls
 */

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
        const animate = () => {
            this.render();
            requestAnimationFrame(animate);
        };
        animate();
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

function updateButtonStates() {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    if (trainingActive) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

function startTraining() {
    trainingActive = true;
    updateButtonStates();
    console.log('Training started');
    // WebSocket integration will be added in Plan 03
}

function stopTraining() {
    trainingActive = false;
    updateButtonStates();
    console.log('Training stopped');
    // WebSocket integration will be added in Plan 03
}

function resetTraining() {
    trainingActive = false;
    updateButtonStates();
    document.getElementById('episode-counter').textContent = '0';
    document.getElementById('step-counter').textContent = '0';
    console.log('Training reset');
    // WebSocket integration will be added in Plan 03
}

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize grid renderer
    const renderer = new GridRenderer('grid-canvas', 5, 50);
    renderer.startAnimationLoop();

    // Make renderer globally accessible for testing
    window.renderer = renderer;

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

    // Initialize button states
    updateButtonStates();
});
