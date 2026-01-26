"""Tests for GridWorld environment."""

import numpy as np
import pytest

from src.gridworld.config import GridWorldConfig
from src.gridworld.environment import GridWorldEnv


class TestGridWorldConfig:
    """Test GridWorldConfig validation."""

    def test_default_config(self):
        """Test that default configuration is valid."""
        config = GridWorldConfig()
        assert config.grid_size == 5
        assert config.start_pos == (0, 0)
        assert config.goal_pos == (4, 4)
        assert config.obstacles == []

    def test_invalid_start_position(self):
        """Test that invalid start position raises error."""
        with pytest.raises(ValueError, match="Start position .* outside grid"):
            GridWorldConfig(grid_size=5, start_pos=(5, 5))

    def test_invalid_goal_position(self):
        """Test that invalid goal position raises error."""
        with pytest.raises(ValueError, match="Goal position .* outside grid"):
            GridWorldConfig(grid_size=5, goal_pos=(10, 10))

    def test_invalid_obstacle_position(self):
        """Test that invalid obstacle position raises error."""
        with pytest.raises(ValueError, match="Obstacle position .* outside grid"):
            GridWorldConfig(grid_size=5, obstacles=[(6, 6)])

    def test_start_equals_goal(self):
        """Test that start position cannot equal goal position."""
        with pytest.raises(ValueError, match="Start and goal positions cannot be the same"):
            GridWorldConfig(start_pos=(2, 2), goal_pos=(2, 2))


class TestGridWorldEnv:
    """Test GridWorld environment."""

    def test_initialization(self):
        """Test environment initializes correctly."""
        env = GridWorldEnv()
        assert env.action_space.n == 4
        assert env.observation_space.shape == (2,)
        assert env.num_states == 25  # 5x5 grid
        assert env.num_actions == 4

    def test_reset(self):
        """Test environment reset."""
        config = GridWorldConfig(start_pos=(1, 2))
        env = GridWorldEnv(config)

        obs, info = env.reset()
        assert np.array_equal(obs, np.array([1, 2]))
        assert env.step_count == 0
        assert isinstance(info, dict)

    def test_step_up(self):
        """Test moving up."""
        config = GridWorldConfig(start_pos=(2, 2), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.UP)

        assert np.array_equal(obs, np.array([2, 1]))  # y decreases
        assert reward == config.step_penalty
        assert not terminated
        assert not truncated

    def test_step_down(self):
        """Test moving down."""
        config = GridWorldConfig(start_pos=(2, 2), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.DOWN)

        assert np.array_equal(obs, np.array([2, 3]))  # y increases
        assert reward == config.step_penalty
        assert not terminated

    def test_step_left(self):
        """Test moving left."""
        config = GridWorldConfig(start_pos=(2, 2), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.LEFT)

        assert np.array_equal(obs, np.array([1, 2]))  # x decreases
        assert reward == config.step_penalty
        assert not terminated

    def test_step_right(self):
        """Test moving right."""
        config = GridWorldConfig(start_pos=(2, 2), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.RIGHT)

        assert np.array_equal(obs, np.array([3, 2]))  # x increases
        assert reward == config.step_penalty
        assert not terminated

    def test_boundary_top(self):
        """Test that agent cannot move beyond top boundary."""
        config = GridWorldConfig(start_pos=(2, 0), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, _, _, _, _ = env.step(GridWorldEnv.UP)
        assert np.array_equal(obs, np.array([2, 0]))  # Stays at boundary

    def test_boundary_bottom(self):
        """Test that agent cannot move beyond bottom boundary."""
        config = GridWorldConfig(start_pos=(2, 4), goal_pos=(0, 0))
        env = GridWorldEnv(config)
        env.reset()

        obs, _, _, _, _ = env.step(GridWorldEnv.DOWN)
        assert np.array_equal(obs, np.array([2, 4]))  # Stays at boundary

    def test_boundary_left(self):
        """Test that agent cannot move beyond left boundary."""
        config = GridWorldConfig(start_pos=(0, 2), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, _, _, _, _ = env.step(GridWorldEnv.LEFT)
        assert np.array_equal(obs, np.array([0, 2]))  # Stays at boundary

    def test_boundary_right(self):
        """Test that agent cannot move beyond right boundary."""
        config = GridWorldConfig(start_pos=(4, 2), goal_pos=(0, 0))
        env = GridWorldEnv(config)
        env.reset()

        obs, _, _, _, _ = env.step(GridWorldEnv.RIGHT)
        assert np.array_equal(obs, np.array([4, 2]))  # Stays at boundary

    def test_reach_goal(self):
        """Test that reaching goal gives correct reward and terminates."""
        config = GridWorldConfig(start_pos=(3, 4), goal_pos=(4, 4))
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.RIGHT)

        assert np.array_equal(obs, np.array([4, 4]))
        assert reward == config.goal_reward
        assert terminated
        assert not truncated
        assert info["is_goal"]

    def test_hit_obstacle(self):
        """Test that hitting obstacle gives correct penalty and terminates."""
        config = GridWorldConfig(start_pos=(1, 2), goal_pos=(4, 4), obstacles=[(2, 2)])
        env = GridWorldEnv(config)
        env.reset()

        obs, reward, terminated, truncated, info = env.step(GridWorldEnv.RIGHT)

        assert np.array_equal(obs, np.array([2, 2]))
        assert reward == config.obstacle_penalty
        assert terminated
        assert not truncated
        assert info["is_obstacle"]

    def test_max_steps_truncation(self):
        """Test that episode truncates after max steps."""
        config = GridWorldConfig(start_pos=(0, 0), goal_pos=(4, 4), max_steps=3)
        env = GridWorldEnv(config)
        env.reset()

        # Take 3 steps
        for _ in range(2):
            _, _, terminated, truncated, _ = env.step(GridWorldEnv.RIGHT)
            assert not terminated
            assert not truncated

        # Third step should trigger truncation
        _, _, terminated, truncated, _ = env.step(GridWorldEnv.RIGHT)
        assert not terminated
        assert truncated

    def test_invalid_action(self):
        """Test that invalid action raises error."""
        env = GridWorldEnv()
        env.reset()

        with pytest.raises(ValueError, match="Invalid action"):
            env.step(5)

    def test_step_before_reset(self):
        """Test that stepping before reset raises error."""
        env = GridWorldEnv()

        with pytest.raises(RuntimeError, match="Environment not initialized"):
            env.step(GridWorldEnv.UP)

    def test_state_index_conversion(self):
        """Test converting between position and state index."""
        config = GridWorldConfig(grid_size=5)
        env = GridWorldEnv(config)

        # Test various positions
        assert env.get_state_index((0, 0)) == 0
        assert env.get_state_index((4, 0)) == 4
        assert env.get_state_index((0, 1)) == 5
        assert env.get_state_index((4, 4)) == 24

        # Test reverse conversion
        assert env.get_position_from_index(0) == (0, 0)
        assert env.get_position_from_index(4) == (4, 0)
        assert env.get_position_from_index(5) == (0, 1)
        assert env.get_position_from_index(24) == (4, 4)

    def test_state_index_with_current_position(self):
        """Test getting state index of current agent position."""
        config = GridWorldConfig(start_pos=(2, 3))
        env = GridWorldEnv(config)
        env.reset()

        assert env.get_state_index() == 17  # 3*5 + 2

    def test_render(self):
        """Test that render doesn't crash."""
        config = GridWorldConfig(start_pos=(0, 0), goal_pos=(4, 4), obstacles=[(2, 2)])
        env = GridWorldEnv(config)
        env.reset()

        # Just check it doesn't crash
        result = env.render()
        assert isinstance(result, str)
        assert "A" in result  # Agent
        assert "G" in result  # Goal
        assert "X" in result  # Obstacle

    def test_multiple_episodes(self):
        """Test running multiple episodes."""
        env = GridWorldEnv()

        for _ in range(3):
            obs, _ = env.reset()
            assert np.array_equal(obs, np.array([0, 0]))

            # Take a few steps
            for _ in range(5):
                obs, reward, terminated, truncated, _ = env.step(GridWorldEnv.RIGHT)
                if terminated or truncated:
                    break

    def test_reproducibility_with_seed(self):
        """Test that setting seed makes environment deterministic."""
        env = GridWorldEnv()

        # Run episode with seed
        env.reset(seed=42)
        states1 = [tuple(env.agent_pos)]
        for _ in range(5):
            env.step(GridWorldEnv.RIGHT)
            states1.append(tuple(env.agent_pos))

        # Run again with same seed
        env.reset(seed=42)
        states2 = [tuple(env.agent_pos)]
        for _ in range(5):
            env.step(GridWorldEnv.RIGHT)
            states2.append(tuple(env.agent_pos))

        assert states1 == states2
