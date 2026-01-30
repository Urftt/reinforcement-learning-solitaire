"""Q-learning agent implementation for GridWorld environment."""

import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np

from src.gridworld.config import QLearningConfig


class QLearningAgent:
    """Q-learning agent with epsilon-greedy policy and Q-table persistence.

    Implements tabular Q-learning algorithm with:
    - Epsilon-greedy action selection
    - Q-value updates using Bellman equation
    - Epsilon decay over training episodes
    - Q-table save/load for training continuity

    Attributes:
        config: QLearningConfig with hyperparameters
        grid_size: Size of the grid (for Q-table dimensions)
        q_table: 3D numpy array (grid_size x grid_size x 4 actions)
        epsilon: Current exploration rate (decays over time)
    """

    # Action encoding (matches environment conventions)
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def __init__(self, config: QLearningConfig, grid_size: int):
        """Initialize Q-learning agent.

        Args:
            config: QLearningConfig with learning parameters
            grid_size: Size of the square grid (e.g., 5 for 5x5 grid)
        """
        self.config = config
        self.grid_size = grid_size

        # Initialize Q-table with zeros: (x, y, action)
        # Shape: (grid_size, grid_size, 4) for 4 actions
        self.q_table = np.zeros((grid_size, grid_size, 4), dtype=np.float32)

        # Initialize epsilon from config
        self.epsilon = config.epsilon_start

    def select_action(self, state: tuple[int, int]) -> int:
        """Select action using epsilon-greedy policy.

        With probability epsilon, selects random action (exploration).
        Otherwise, selects action with highest Q-value (exploitation).

        Args:
            state: Current state as (x, y) tuple

        Returns:
            Action index (0=up, 1=down, 2=left, 3=right)
        """
        # Exploration: random action
        if np.random.random() < self.epsilon:
            return np.random.randint(0, 4)

        # Exploitation: greedy action (highest Q-value)
        x, y = state
        return int(np.argmax(self.q_table[x, y]))

    def update(
        self,
        state: tuple[int, int],
        action: int,
        reward: float,
        next_state: tuple[int, int],
        done: bool,
    ):
        """Update Q-table using Q-learning formula.

        Q(s,a) ← Q(s,a) + α[r + γ max_a' Q(s',a') - Q(s,a)]

        Args:
            state: Current state (x, y)
            action: Action taken (0-3)
            reward: Reward received
            next_state: Next state (x, y)
            done: Whether episode terminated
        """
        x, y = state
        next_x, next_y = next_state

        # Current Q-value
        current_q = self.q_table[x, y, action]

        # Maximum Q-value for next state (0 if terminal)
        if done:
            max_next_q = 0.0
        else:
            max_next_q = np.max(self.q_table[next_x, next_y])

        # Q-learning update
        # Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        new_q = current_q + self.config.learning_rate * (
            reward + self.config.discount_factor * max_next_q - current_q
        )

        self.q_table[x, y, action] = new_q

    def decay_epsilon(self):
        """Decay epsilon using exponential decay.

        Multiplies epsilon by epsilon_decay, ensuring it doesn't drop below epsilon_end.
        """
        self.epsilon = max(
            self.config.epsilon_end, self.epsilon * self.config.epsilon_decay
        )

    def get_q_values(self, state: tuple[int, int]) -> np.ndarray:
        """Get Q-values for all actions in a given state.

        Useful for visualization and debugging.

        Args:
            state: State (x, y) to query

        Returns:
            Array of 4 Q-values [up, down, left, right]
        """
        x, y = state
        return self.q_table[x, y].copy()

    def save_q_table(self, filepath: str):
        """Save Q-table and agent state to JSON file.

        Saves Q-table as nested lists with metadata for restoration.
        Creates directory if it doesn't exist.

        Args:
            filepath: Path to save file (e.g., '.qtables/agent_latest.json')
        """
        # Create directory if needed
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Convert Q-table to JSON-serializable format
        data = {
            "q_table": self.q_table.tolist(),
            "epsilon": float(self.epsilon),
            "grid_size": self.grid_size,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "config": {
                "learning_rate": self.config.learning_rate,
                "discount_factor": self.config.discount_factor,
                "epsilon_decay": self.config.epsilon_decay,
            },
        }

        # Write to file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_q_table(self, filepath: str) -> bool:
        """Load Q-table and agent state from JSON file.

        Restores Q-table and epsilon value from saved state.
        Validates grid_size matches current configuration.

        Args:
            filepath: Path to load file (e.g., '.qtables/agent_latest.json')

        Returns:
            True if load successful, False if file doesn't exist
        """
        if not os.path.exists(filepath):
            return False

        # Load JSON data
        with open(filepath) as f:
            data = json.load(f)

        # Validate grid size matches
        if data["grid_size"] != self.grid_size:
            raise ValueError(
                f"Grid size mismatch: saved={data['grid_size']}, "
                f"current={self.grid_size}"
            )

        # Restore Q-table and epsilon
        self.q_table = np.array(data["q_table"], dtype=np.float32)
        self.epsilon = data["epsilon"]

        return True
