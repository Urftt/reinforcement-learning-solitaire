"""Tests for Q-learning agent."""

import tempfile
from pathlib import Path

import numpy as np

from src.gridworld.agent import QLearningAgent
from src.gridworld.config import QLearningConfig
from src.gridworld.environment import GridWorldEnv


class TestQLearningAgent:
    """Test Q-learning agent."""

    def test_initialization(self):
        """Test agent initializes correctly."""
        agent = QLearningAgent(num_states=25, num_actions=4)

        assert agent.num_states == 25
        assert agent.num_actions == 4
        assert agent.q_table.shape == (25, 4)
        assert np.all(agent.q_table == 0)  # Q-table starts at zeros
        assert agent.epsilon == 1.0  # Default epsilon_start

    def test_initialization_with_config(self):
        """Test agent initialization with custom config."""
        config = QLearningConfig(
            learning_rate=0.5,
            discount_factor=0.95,
            epsilon_start=0.8,
            epsilon_end=0.05,
            epsilon_decay=0.99,
        )
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        assert agent.config.learning_rate == 0.5
        assert agent.config.discount_factor == 0.95
        assert agent.epsilon == 0.8

    def test_select_action_exploitation(self):
        """Test action selection in exploitation mode (epsilon=0)."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.epsilon = 0.0  # Pure exploitation

        # Set Q-values so action 2 is best
        agent.q_table[0] = [1.0, 2.0, 5.0, 3.0]

        # Should always select action 2
        for _ in range(10):
            action = agent.select_action(state_index=0, training=True)
            assert action == 2

    def test_select_action_exploration(self):
        """Test action selection in exploration mode (epsilon=1)."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.epsilon = 1.0  # Pure exploration

        # Set Q-values so action 2 is best
        agent.q_table[0] = [1.0, 2.0, 5.0, 3.0]

        # Should explore (select random actions)
        # With epsilon=1, actions should be random
        actions = [agent.select_action(state_index=0, training=True) for _ in range(100)]

        # Should have at least 2 different actions (very high probability)
        assert len(set(actions)) >= 2

    def test_select_action_eval_mode(self):
        """Test action selection in evaluation mode (training=False)."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.epsilon = 1.0  # High epsilon, but should be ignored in eval mode

        # Set Q-values so action 3 is best
        agent.q_table[0] = [1.0, 2.0, 3.0, 5.0]

        # Should always select action 3 (greedy) even with high epsilon
        for _ in range(10):
            action = agent.select_action(state_index=0, training=False)
            assert action == 3

    def test_learn_basic_update(self):
        """Test Q-value update with simple scenario."""
        config = QLearningConfig(learning_rate=0.1, discount_factor=0.9)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        # Initial Q-values
        agent.q_table[0] = [0.0, 0.0, 0.0, 0.0]
        agent.q_table[1] = [1.0, 2.0, 3.0, 4.0]

        # Take action 0 from state 0, get reward 5, transition to state 1
        td_error = agent.learn(
            state_index=0, action=0, reward=5.0, next_state_index=1, terminated=False
        )

        # Expected: Q(0, 0) = 0 + 0.1 * [5 + 0.9 * 4.0 - 0] = 0.86
        expected_q = 0.1 * (5.0 + 0.9 * 4.0)
        assert abs(agent.q_table[0, 0] - expected_q) < 1e-6
        assert abs(td_error - (5.0 + 0.9 * 4.0)) < 1e-6

    def test_learn_terminal_state(self):
        """Test Q-value update for terminal state (no future value)."""
        config = QLearningConfig(learning_rate=0.1, discount_factor=0.9)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        # Initial Q-values
        agent.q_table[0] = [0.0, 0.0, 0.0, 0.0]

        # Take action 0, get reward 10 (goal), episode terminates
        td_error = agent.learn(
            state_index=0, action=0, reward=10.0, next_state_index=24, terminated=True
        )

        # Expected: Q(0, 0) = 0 + 0.1 * [10 + 0 - 0] = 1.0
        # (no future value because terminal)
        expected_q = 0.1 * 10.0
        assert abs(agent.q_table[0, 0] - expected_q) < 1e-6
        assert abs(td_error - 10.0) < 1e-6

    def test_learn_multiple_updates(self):
        """Test multiple Q-value updates accumulate correctly."""
        config = QLearningConfig(learning_rate=1.0, discount_factor=0.0)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        # With learning_rate=1.0 and discount_factor=0.0,
        # Q-value should exactly equal the immediate reward

        agent.learn(state_index=0, action=0, reward=5.0, next_state_index=1, terminated=True)
        assert abs(agent.q_table[0, 0] - 5.0) < 1e-6

        agent.learn(state_index=0, action=1, reward=3.0, next_state_index=1, terminated=True)
        assert abs(agent.q_table[0, 1] - 3.0) < 1e-6

    def test_decay_epsilon(self):
        """Test epsilon decay."""
        config = QLearningConfig(epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.9)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        assert agent.epsilon == 1.0

        agent.decay_epsilon()
        assert abs(agent.epsilon - 0.9) < 1e-6

        agent.decay_epsilon()
        assert abs(agent.epsilon - 0.81) < 1e-6

        # Decay many times
        for _ in range(100):
            agent.decay_epsilon()

        # Should not go below epsilon_end
        assert agent.epsilon >= 0.01

    def test_get_q_values(self):
        """Test getting Q-values for a state."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.q_table[5] = [1.0, 2.0, 3.0, 4.0]

        q_values = agent.get_q_values(state_index=5)
        assert np.array_equal(q_values, np.array([1.0, 2.0, 3.0, 4.0]))

        # Should return a copy, not reference
        q_values[0] = 999.0
        assert agent.q_table[5, 0] == 1.0

    def test_get_policy(self):
        """Test extracting greedy policy."""
        agent = QLearningAgent(num_states=4, num_actions=4)

        # Set Q-values for each state
        agent.q_table[0] = [1.0, 2.0, 3.0, 4.0]  # Best action: 3
        agent.q_table[1] = [5.0, 2.0, 3.0, 1.0]  # Best action: 0
        agent.q_table[2] = [1.0, 9.0, 3.0, 4.0]  # Best action: 1
        agent.q_table[3] = [1.0, 2.0, 8.0, 4.0]  # Best action: 2

        policy = agent.get_policy()
        assert np.array_equal(policy, np.array([3, 0, 1, 2]))

    def test_get_state_value(self):
        """Test getting state value V(s) = max_a Q(s, a)."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.q_table[5] = [1.0, 2.0, 5.0, 3.0]

        state_value = agent.get_state_value(state_index=5)
        assert state_value == 5.0

    def test_save_and_load(self):
        """Test saving and loading agent."""
        config = QLearningConfig(learning_rate=0.2, discount_factor=0.95)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        # Set some Q-values and decay epsilon
        agent.q_table[0] = [1.0, 2.0, 3.0, 4.0]
        agent.q_table[5] = [5.0, 6.0, 7.0, 8.0]
        agent.epsilon = 0.5

        # Save to temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "agent.pkl"
            agent.save(filepath)

            # Load into new agent
            loaded_agent = QLearningAgent(num_states=25, num_actions=4)
            loaded_agent.load(filepath)

            # Check everything matches
            assert np.array_equal(loaded_agent.q_table, agent.q_table)
            assert loaded_agent.epsilon == agent.epsilon
            assert loaded_agent.config.learning_rate == agent.config.learning_rate
            assert loaded_agent.config.discount_factor == agent.config.discount_factor
            assert loaded_agent.num_states == agent.num_states
            assert loaded_agent.num_actions == agent.num_actions

    def test_load_from_file_classmethod(self):
        """Test loading agent using class method."""
        config = QLearningConfig(learning_rate=0.3, discount_factor=0.8)
        agent = QLearningAgent(num_states=25, num_actions=4, config=config)

        agent.q_table[0] = [1.0, 2.0, 3.0, 4.0]
        agent.epsilon = 0.3

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "agent.pkl"
            agent.save(filepath)

            # Load using class method
            loaded_agent = QLearningAgent.load_from_file(filepath)

            assert np.array_equal(loaded_agent.q_table, agent.q_table)
            assert loaded_agent.epsilon == agent.epsilon
            assert loaded_agent.config.learning_rate == 0.3

    def test_reset_q_table(self):
        """Test resetting Q-table."""
        agent = QLearningAgent(num_states=25, num_actions=4)

        # Set some values
        agent.q_table[0] = [1.0, 2.0, 3.0, 4.0]
        agent.epsilon = 0.2

        # Reset
        agent.reset_q_table()

        # Q-table should be zeros, epsilon should be reset
        assert np.all(agent.q_table == 0)
        assert agent.epsilon == 1.0  # Back to epsilon_start

    def test_integration_with_gridworld(self):
        """Test agent working with GridWorld environment."""
        env = GridWorldEnv()
        agent = QLearningAgent(num_states=env.num_states, num_actions=env.num_actions)

        # Run a simple episode
        obs, _ = env.reset(seed=42)
        state_index = env.get_state_index(obs)

        total_reward = 0
        steps = 0
        max_steps = 100

        while steps < max_steps:
            # Select action
            action = agent.select_action(state_index, training=True)

            # Take step
            next_obs, reward, terminated, truncated, _ = env.step(action)
            next_state_index = env.get_state_index(next_obs)
            total_reward += reward

            # Learn
            agent.learn(state_index, action, reward, next_state_index, terminated)

            # Update state
            state_index = next_state_index
            steps += 1

            if terminated or truncated:
                break

        # Just check it runs without errors
        assert steps > 0
        assert steps <= max_steps

    def test_bellman_equation_correctness(self):
        """Test that Bellman equation is implemented correctly."""
        # Use specific values to verify the math
        config = QLearningConfig(learning_rate=0.5, discount_factor=0.9)
        agent = QLearningAgent(num_states=3, num_actions=2, config=config)

        # Initial Q-values
        agent.q_table[0, 0] = 2.0
        agent.q_table[1, 0] = 3.0
        agent.q_table[1, 1] = 5.0  # Max for state 1

        # Transition: state 0, action 0, reward 4, next state 1
        # Q(0,0) = 2.0 + 0.5 * [4 + 0.9 * 5.0 - 2.0]
        #        = 2.0 + 0.5 * [4 + 4.5 - 2.0]
        #        = 2.0 + 0.5 * 6.5
        #        = 2.0 + 3.25
        #        = 5.25

        agent.learn(state_index=0, action=0, reward=4.0, next_state_index=1, terminated=False)

        assert abs(agent.q_table[0, 0] - 5.25) < 1e-6

    def test_action_selection_distribution(self):
        """Test that epsilon-greedy gives approximately correct distribution."""
        agent = QLearningAgent(num_states=25, num_actions=4)
        agent.epsilon = 0.4  # 40% exploration

        # Set Q-values so action 3 is best
        agent.q_table[0] = [1.0, 2.0, 3.0, 10.0]

        # Sample many actions
        num_samples = 10000
        actions = [agent.select_action(state_index=0, training=True) for _ in range(num_samples)]
        action_counts = np.bincount(actions, minlength=4)
        action_probs = action_counts / num_samples

        # Expected probabilities:
        # - Action 3 (greedy): 0.6 + 0.4 * 0.25 = 0.7
        # - Other actions: 0.4 * 0.25 = 0.1 each

        # Allow 5% tolerance due to randomness
        assert abs(action_probs[0] - 0.1) < 0.05
        assert abs(action_probs[1] - 0.1) < 0.05
        assert abs(action_probs[2] - 0.1) < 0.05
        assert abs(action_probs[3] - 0.7) < 0.05
