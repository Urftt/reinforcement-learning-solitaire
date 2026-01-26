"""GridWorld environment implementation using Gymnasium interface."""

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.gridworld.config import GridWorldConfig


class GridWorldEnv(gym.Env):
    """A simple GridWorld environment for reinforcement learning.

    The agent starts at a position and must navigate to a goal while avoiding
    obstacles. Each step incurs a small penalty, obstacles give a large penalty,
    and reaching the goal gives a large reward.

    State space: Discrete (x, y) position on the grid
    Action space: Discrete with 4 actions (up, down, left, right)
    Rewards:
        - Goal: +10 (configurable)
        - Obstacle: -10 (configurable)
        - Step: -1 (configurable)
    """

    # Action constants for readability
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, config: GridWorldConfig = None):
        """Initialize GridWorld environment.

        Args:
            config: GridWorldConfig object with environment parameters
        """
        super().__init__()

        self.config = config if config is not None else GridWorldConfig()

        # Define action and observation spaces (Gymnasium requirement)
        self.action_space = spaces.Discrete(4)  # Up, Down, Left, Right

        # Observation space: (x, y) position
        self.observation_space = spaces.Box(
            low=0,
            high=self.config.grid_size - 1,
            shape=(2,),
            dtype=np.int32
        )

        # Internal state
        self.agent_pos: np.ndarray | None = None
        self.step_count: int = 0

        # Convert obstacles to set for faster lookup
        self._obstacles_set = set(self.config.obstacles)

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset the environment to initial state.

        Args:
            seed: Random seed for reproducibility
            options: Additional options (unused)

        Returns:
            observation: Initial agent position (x, y)
            info: Additional information (empty dict)
        """
        super().reset(seed=seed)

        # Reset agent to start position
        self.agent_pos = np.array(self.config.start_pos, dtype=np.int32)
        self.step_count = 0

        observation = self.agent_pos.copy()
        info = {}

        return observation, info

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Execute one step in the environment.

        Args:
            action: Action to take (0=up, 1=down, 2=left, 3=right)

        Returns:
            observation: New agent position (x, y)
            reward: Reward received
            terminated: Whether episode ended (reached goal or obstacle)
            truncated: Whether episode was truncated (max steps)
            info: Additional information
        """
        if self.agent_pos is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        # Calculate new position based on action
        new_pos = self.agent_pos.copy()

        if action == self.UP:
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == self.DOWN:
            new_pos[1] = min(self.config.grid_size - 1, new_pos[1] + 1)
        elif action == self.LEFT:
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == self.RIGHT:
            new_pos[0] = min(self.config.grid_size - 1, new_pos[0] + 1)
        else:
            raise ValueError(f"Invalid action: {action}. Must be 0-3.")

        # Update agent position
        self.agent_pos = new_pos
        self.step_count += 1

        # Calculate reward and check terminal conditions
        terminated = False
        reward = self.config.step_penalty  # Default step penalty

        # Check if reached goal
        if tuple(self.agent_pos) == self.config.goal_pos:
            reward = self.config.goal_reward
            terminated = True

        # Check if hit obstacle
        elif tuple(self.agent_pos) in self._obstacles_set:
            reward = self.config.obstacle_penalty
            terminated = True

        # Check if exceeded max steps
        truncated = self.step_count >= self.config.max_steps

        observation = self.agent_pos.copy()
        info = {
            "step_count": self.step_count,
            "is_goal": tuple(self.agent_pos) == self.config.goal_pos,
            "is_obstacle": tuple(self.agent_pos) in self._obstacles_set,
        }

        return observation, reward, terminated, truncated, info

    def render(self):
        """Render the environment (simple text-based for now).

        Returns:
            Grid representation as string (if render_mode is 'human')
        """
        # Create grid representation
        grid = np.full((self.config.grid_size, self.config.grid_size), '·', dtype=str)

        # Mark obstacles
        for obs in self.config.obstacles:
            grid[obs[1], obs[0]] = 'X'

        # Mark goal
        grid[self.config.goal_pos[1], self.config.goal_pos[0]] = 'G'

        # Mark agent (overwrites goal if agent is on it)
        if self.agent_pos is not None:
            grid[self.agent_pos[1], self.agent_pos[0]] = 'A'

        # Convert to string
        grid_str = '\n'.join(' '.join(row) for row in grid)
        grid_str = f"\nStep: {self.step_count}\n{grid_str}\n"

        print(grid_str)
        return grid_str

    def get_state_index(self, position: tuple[int, int] | np.ndarray | None = None) -> int:
        """Convert (x, y) position to single state index.

        Useful for tabular Q-learning where we need a single index for the Q-table.

        Args:
            position: (x, y) position. If None, uses current agent position.

        Returns:
            State index: y * grid_size + x
        """
        if position is None:
            if self.agent_pos is None:
                raise RuntimeError("No position provided and environment not initialized")
            position = self.agent_pos

        if isinstance(position, np.ndarray):
            x, y = position[0], position[1]
        else:
            x, y = position

        return int(y * self.config.grid_size + x)

    def get_position_from_index(self, state_index: int) -> tuple[int, int]:
        """Convert state index back to (x, y) position.

        Args:
            state_index: State index

        Returns:
            (x, y) position tuple
        """
        y = state_index // self.config.grid_size
        x = state_index % self.config.grid_size
        return (x, y)

    @property
    def num_states(self) -> int:
        """Total number of possible states.

        Returns:
            grid_size * grid_size
        """
        return self.config.grid_size * self.config.grid_size

    @property
    def num_actions(self) -> int:
        """Total number of possible actions.

        Returns:
            4 (up, down, left, right)
        """
        return 4
