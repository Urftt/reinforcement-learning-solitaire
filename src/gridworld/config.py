"""Configuration for GridWorld environment and Q-learning agent."""

from dataclasses import dataclass


@dataclass
class GridWorldConfig:
    """Configuration for GridWorld environment.

    Attributes:
        grid_size: Size of the square grid (default 5x5)
        start_pos: Starting position of agent (x, y)
        goal_pos: Goal position (x, y)
        obstacles: List of obstacle positions [(x, y), ...]
        goal_reward: Reward for reaching goal
        obstacle_penalty: Penalty for hitting obstacle
        step_penalty: Penalty for each step taken
        max_steps: Maximum steps per episode (prevent infinite loops)
    """

    grid_size: int = 5
    start_pos: tuple[int, int] = (0, 0)
    goal_pos: tuple[int, int] = (4, 4)
    obstacles: list[tuple[int, int]] = None
    goal_reward: float = 10.0
    obstacle_penalty: float = -10.0
    step_penalty: float = -0.1  # Small penalty to encourage efficiency
    max_steps: int = 100

    def __post_init__(self):
        """Validate configuration and set defaults."""
        if self.obstacles is None:
            self.obstacles = []

        # Validate positions are within grid
        if not (
            0 <= self.start_pos[0] < self.grid_size and 0 <= self.start_pos[1] < self.grid_size
        ):
            raise ValueError(f"Start position {self.start_pos} outside grid")

        if not (0 <= self.goal_pos[0] < self.grid_size and 0 <= self.goal_pos[1] < self.grid_size):
            raise ValueError(f"Goal position {self.goal_pos} outside grid")

        # Validate obstacles
        for obs in self.obstacles:
            if not (0 <= obs[0] < self.grid_size and 0 <= obs[1] < self.grid_size):
                raise ValueError(f"Obstacle position {obs} outside grid")

        # Ensure start != goal
        if self.start_pos == self.goal_pos:
            raise ValueError("Start and goal positions cannot be the same")


@dataclass
class QLearningConfig:
    """Configuration for Q-learning agent.

    Attributes:
        learning_rate: Step size for Q-value updates (alpha)
        discount_factor: Future reward discount (gamma)
        epsilon_start: Initial exploration rate
        epsilon_end: Final exploration rate
        epsilon_decay: Decay rate for epsilon
        num_episodes: Number of training episodes
    """

    learning_rate: float = 0.1
    discount_factor: float = 0.99
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    num_episodes: int = 500
