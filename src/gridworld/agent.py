"""Q-learning agent implementation for GridWorld."""

import pickle
from pathlib import Path

import numpy as np

from src.gridworld.config import QLearningConfig


class QLearningAgent:
    """Tabular Q-learning agent using epsilon-greedy exploration.

    This agent learns to navigate the GridWorld environment by maintaining a Q-table
    (state-action value function) and updating it using the Bellman equation:

        Q(s, a) ← Q(s, a) + α * [r + γ * max_a' Q(s', a') - Q(s, a)]

    Where:
        - α (alpha) is the learning rate
        - γ (gamma) is the discount factor
        - r is the immediate reward
        - s' is the next state
        - max_a' Q(s', a') is the maximum Q-value for the next state

    Attributes:
        config: QLearningConfig with hyperparameters
        q_table: NumPy array of shape [num_states, num_actions] storing Q-values
        epsilon: Current exploration rate (decays over time)
        num_states: Number of possible states in the environment
        num_actions: Number of possible actions in the environment
    """

    def __init__(self, num_states: int, num_actions: int, config: QLearningConfig = None):
        """Initialize Q-learning agent.

        Args:
            num_states: Number of possible states in the environment
            num_actions: Number of possible actions in the environment
            config: QLearningConfig object with hyperparameters
        """
        self.config = config if config is not None else QLearningConfig()
        self.num_states = num_states
        self.num_actions = num_actions

        # Initialize Q-table with zeros
        # Shape: [num_states, num_actions]
        self.q_table = np.zeros((num_states, num_actions), dtype=np.float32)

        # Initialize exploration rate
        self.epsilon = self.config.epsilon_start

    def select_action(self, state_index: int, training: bool = True) -> int:
        """Select action using epsilon-greedy policy.

        During training, with probability epsilon, select a random action (exploration).
        Otherwise, select the action with the highest Q-value (exploitation).

        During evaluation (training=False), always select the greedy action.

        Args:
            state_index: Current state index
            training: If True, use epsilon-greedy. If False, use greedy policy.

        Returns:
            Selected action (0-3 for GridWorld: up, down, left, right)
        """
        # Epsilon-greedy exploration (only during training)
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.randint(self.num_actions)
        else:
            # Exploit: greedy action (highest Q-value)
            return int(np.argmax(self.q_table[state_index]))

    def learn(
        self,
        state_index: int,
        action: int,
        reward: float,
        next_state_index: int,
        terminated: bool,
    ) -> float:
        """Update Q-value using the Bellman equation.

        Implements the Q-learning update rule:
            Q(s, a) ← Q(s, a) + α * [r + γ * max_a' Q(s', a') - Q(s, a)]

        For terminal states, the future value is 0 (no next state).

        Args:
            state_index: Current state index
            action: Action taken
            reward: Reward received
            next_state_index: Next state index
            terminated: Whether the episode terminated (reached goal or obstacle)

        Returns:
            TD error (temporal difference error): r + γ * max_a' Q(s', a') - Q(s, a)
        """
        # Current Q-value
        current_q = self.q_table[state_index, action]

        # Maximum Q-value for next state (0 if terminal)
        if terminated:
            max_next_q = 0.0
        else:
            max_next_q = np.max(self.q_table[next_state_index])

        # Bellman equation: TD target = r + γ * max_a' Q(s', a')
        td_target = reward + self.config.discount_factor * max_next_q

        # TD error: how much we need to update
        td_error = td_target - current_q

        # Update Q-value: Q(s, a) ← Q(s, a) + α * TD_error
        self.q_table[state_index, action] += self.config.learning_rate * td_error

        return td_error

    def decay_epsilon(self) -> None:
        """Decay epsilon (exploration rate) after each episode.

        Uses exponential decay: epsilon ← epsilon * decay_rate
        Ensures epsilon never goes below epsilon_end.
        """
        self.epsilon = max(self.config.epsilon_end, self.epsilon * self.config.epsilon_decay)

    def get_q_values(self, state_index: int) -> np.ndarray:
        """Get Q-values for a specific state.

        Args:
            state_index: State index

        Returns:
            Array of Q-values for each action in the given state
        """
        return self.q_table[state_index].copy()

    def get_policy(self) -> np.ndarray:
        """Extract greedy policy from Q-table.

        The policy is deterministic: for each state, select the action with highest Q-value.

        Returns:
            Array of shape [num_states] where each element is the best action for that state
        """
        return np.argmax(self.q_table, axis=1)

    def get_state_value(self, state_index: int) -> float:
        """Get state value V(s) = max_a Q(s, a).

        Args:
            state_index: State index

        Returns:
            Maximum Q-value for the state (state value)
        """
        return float(np.max(self.q_table[state_index]))

    def save(self, filepath: str | Path) -> None:
        """Save Q-table and agent configuration to disk.

        Args:
            filepath: Path to save the agent (will create parent directories if needed)
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save Q-table, config, and epsilon
        save_dict = {
            "q_table": self.q_table,
            "config": self.config,
            "epsilon": self.epsilon,
            "num_states": self.num_states,
            "num_actions": self.num_actions,
        }

        with open(filepath, "wb") as f:
            pickle.dump(save_dict, f)

    def load(self, filepath: str | Path) -> None:
        """Load Q-table and agent configuration from disk.

        Args:
            filepath: Path to the saved agent file
        """
        filepath = Path(filepath)

        with open(filepath, "rb") as f:
            save_dict = pickle.load(f)

        # Restore agent state
        self.q_table = save_dict["q_table"]
        self.config = save_dict["config"]
        self.epsilon = save_dict["epsilon"]
        self.num_states = save_dict["num_states"]
        self.num_actions = save_dict["num_actions"]

    @classmethod
    def load_from_file(cls, filepath: str | Path) -> "QLearningAgent":
        """Load a saved agent from disk (class method).

        Args:
            filepath: Path to the saved agent file

        Returns:
            Loaded QLearningAgent instance
        """
        filepath = Path(filepath)

        with open(filepath, "rb") as f:
            save_dict = pickle.load(f)

        # Create new agent instance
        agent = cls(
            num_states=save_dict["num_states"],
            num_actions=save_dict["num_actions"],
            config=save_dict["config"],
        )

        # Restore state
        agent.q_table = save_dict["q_table"]
        agent.epsilon = save_dict["epsilon"]

        return agent

    def reset_q_table(self) -> None:
        """Reset Q-table to zeros (useful for starting fresh training)."""
        self.q_table = np.zeros((self.num_states, self.num_actions), dtype=np.float32)
        self.epsilon = self.config.epsilon_start
