"""Demo script for GridWorld environment.

This will be replaced with actual training code in Feature 1.2.
For now, it demonstrates the environment with a random policy.
"""

import numpy as np

from src.gridworld.config import GridWorldConfig
from src.gridworld.environment import GridWorldEnv


def demo_random_agent(num_episodes: int = 3):
    """Run a simple demo with a random agent.

    Args:
        num_episodes: Number of episodes to run
    """
    # Create environment with some obstacles
    config = GridWorldConfig(
        grid_size=5,
        start_pos=(0, 0),
        goal_pos=(4, 4),
        obstacles=[(2, 2), (3, 1)],
        max_steps=50
    )

    env = GridWorldEnv(config)

    print("=" * 50)
    print("GridWorld Environment Demo")
    print("=" * 50)
    print(f"\nGrid size: {config.grid_size}x{config.grid_size}")
    print(f"Start: {config.start_pos}")
    print(f"Goal: {config.goal_pos}")
    print(f"Obstacles: {config.obstacles}")
    print(f"\nRewards:")
    print(f"  Goal: {config.goal_reward}")
    print(f"  Obstacle: {config.obstacle_penalty}")
    print(f"  Step: {config.step_penalty}")
    print("\nActions: 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT")
    print("\nLegend: A=Agent, G=Goal, X=Obstacle, ·=Empty")
    print("=" * 50)

    for episode in range(num_episodes):
        print(f"\n{'=' * 50}")
        print(f"Episode {episode + 1}")
        print('=' * 50)

        obs, info = env.reset(seed=42 + episode)
        print("\nInitial state:")
        env.render()

        total_reward = 0
        done = False
        step_count = 0

        while not done:
            # Random action (this is not learning, just random!)
            action = env.action_space.sample()
            action_names = ["UP", "DOWN", "LEFT", "RIGHT"]

            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            total_reward += reward
            step_count += 1

            print(f"\nAction: {action_names[action]}")
            print(f"Reward: {reward:.1f}")
            env.render()

            if terminated:
                if info["is_goal"]:
                    print("\n🎯 Reached goal!")
                elif info["is_obstacle"]:
                    print("\n💥 Hit obstacle!")
            elif truncated:
                print("\n⏱️  Max steps reached!")

        print(f"\nEpisode summary:")
        print(f"  Total steps: {step_count}")
        print(f"  Total reward: {total_reward:.1f}")


if __name__ == "__main__":
    # Run the demo
    demo_random_agent(num_episodes=3)
