"""Interactive GridWorld game - Play manually to understand the environment."""

import sys
from typing import Literal

from src.gridworld.config import GridWorldConfig
from src.gridworld.environment import GridWorldEnv


def get_action_from_key(key: str) -> int | None:
    """Convert keyboard input to action.

    Args:
        key: User input key

    Returns:
        Action integer or None if invalid
    """
    key_map = {
        "w": GridWorldEnv.UP,
        "a": GridWorldEnv.LEFT,
        "s": GridWorldEnv.DOWN,
        "d": GridWorldEnv.RIGHT,
        "8": GridWorldEnv.UP,
        "4": GridWorldEnv.LEFT,
        "2": GridWorldEnv.DOWN,
        "6": GridWorldEnv.RIGHT,
    }
    return key_map.get(key.lower())


def print_instructions():
    """Print game instructions."""
    print("\n" + "=" * 60)
    print("🎮 GRIDWORLD - MANUAL PLAY MODE")
    print("=" * 60)
    print("\nControls:")
    print("  W/8 = Move UP")
    print("  A/4 = Move LEFT")
    print("  S/2 = Move DOWN")
    print("  D/6 = Move RIGHT")
    print("  Q   = Quit game")
    print("  R   = Restart episode")
    print("\nLegend:")
    print("  A = Agent (you!)")
    print("  G = Goal (reach this!)")
    print("  X = Obstacle (avoid!)")
    print("  · = Empty space")
    print("\nObjective:")
    print("  Navigate to the goal while avoiding obstacles!")
    print("=" * 60)


def print_stats(
    episode: int, step_count: int, total_reward: float, last_reward: float | None = None
):
    """Print current game statistics.

    Args:
        episode: Current episode number
        step_count: Number of steps taken
        total_reward: Cumulative reward
        last_reward: Reward from last action
    """
    print(f"\nEpisode: {episode} | Steps: {step_count} | Total Reward: {total_reward:.1f}", end="")
    if last_reward is not None:
        print(f" | Last: {last_reward:+.1f}", end="")
    print()


def play_gridworld(
    config: GridWorldConfig | None = None, difficulty: Literal["easy", "medium", "hard"] = "medium"
):
    """Interactive GridWorld game.

    Args:
        config: Custom GridWorld configuration (optional)
        difficulty: Preset difficulty level
    """
    # Create environment based on difficulty
    if config is None:
        if difficulty == "easy":
            config = GridWorldConfig(
                grid_size=5,
                start_pos=(0, 0),
                goal_pos=(4, 4),
                obstacles=[],  # No obstacles
                max_steps=50,
            )
        elif difficulty == "medium":
            config = GridWorldConfig(
                grid_size=5,
                start_pos=(0, 0),
                goal_pos=(4, 4),
                obstacles=[(2, 2), (3, 1)],
                max_steps=50,
            )
        else:  # hard
            config = GridWorldConfig(
                grid_size=7,
                start_pos=(0, 0),
                goal_pos=(6, 6),
                obstacles=[(2, 2), (3, 1), (4, 4), (5, 3), (1, 5), (3, 5)],
                max_steps=100,
            )

    env = GridWorldEnv(config)

    print_instructions()
    print(f"\nDifficulty: {difficulty.upper()}")
    print(f"Grid size: {config.grid_size}x{config.grid_size}")
    print(f"Obstacles: {len(config.obstacles)}")
    print(
        f"\nRewards: Goal={config.goal_reward:+.0f}, "
        f"Obstacle={config.obstacle_penalty:+.0f}, "
        f"Step={config.step_penalty:+.0f}"
    )

    episode = 1
    total_reward = 0.0
    obs, _ = env.reset()

    print("\n" + "=" * 60)
    print("STARTING GAME - Good luck!")
    print("=" * 60)
    env.render()
    print_stats(episode, 0, total_reward)

    while True:
        # Get user input
        try:
            user_input = input("\nYour move (wasd/8426, q=quit, r=restart): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Thanks for playing!")
            break

        if not user_input:
            continue

        # Handle special commands
        if user_input.lower() == "q":
            print("\n👋 Thanks for playing!")
            break

        if user_input.lower() == "r":
            print("\n🔄 Restarting episode...")
            episode += 1
            total_reward = 0.0
            obs, _ = env.reset()
            env.render()
            print_stats(episode, 0, total_reward)
            continue

        # Convert input to action
        action = get_action_from_key(user_input)
        if action is None:
            print("❌ Invalid input! Use WASD or 8426 for movement.")
            continue

        # Execute action
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        # Render environment
        env.render()
        print_stats(episode, info["step_count"], total_reward, reward)

        # Check if episode ended
        if terminated:
            if info["is_goal"]:
                print("\n" + "=" * 60)
                print("🎯 CONGRATULATIONS! You reached the goal!")
                print(f"   Final score: {total_reward:.1f}")
                print(f"   Steps taken: {info['step_count']}")
                print("=" * 60)

                # Calculate efficiency
                optimal_steps = abs(config.goal_pos[0] - config.start_pos[0]) + abs(
                    config.goal_pos[1] - config.start_pos[1]
                )
                if info["step_count"] == optimal_steps:
                    print("⭐ PERFECT! You found the optimal path!")
                elif info["step_count"] <= optimal_steps + 3:
                    print("✨ Excellent! Very efficient path!")
                else:
                    print(f"💡 Hint: The optimal path is {optimal_steps} steps")

            elif info["is_obstacle"]:
                print("\n" + "=" * 60)
                print("💥 OUCH! You hit an obstacle!")
                print(f"   Final score: {total_reward:.1f}")
                print(f"   Steps survived: {info['step_count']}")
                print("=" * 60)

            # Ask to continue
            choice = input("\nPlay again? (y/n/d=change difficulty): ").strip().lower()
            if choice == "n":
                print("\n👋 Thanks for playing!")
                break
            elif choice == "d":
                print("\nChoose difficulty:")
                print("  1. Easy   (5x5, no obstacles)")
                print("  2. Medium (5x5, 2 obstacles)")
                print("  3. Hard   (7x7, 6 obstacles)")
                diff_choice = input("Select (1/2/3): ").strip()

                if diff_choice == "1":
                    difficulty = "easy"
                elif diff_choice == "3":
                    difficulty = "hard"
                else:
                    difficulty = "medium"

                # Restart with new difficulty
                return play_gridworld(difficulty=difficulty)
            else:
                episode += 1
                total_reward = 0.0
                obs, _ = env.reset()
                print("\n🔄 Starting new episode...")
                env.render()
                print_stats(episode, 0, total_reward)

        elif truncated:
            print("\n" + "=" * 60)
            print("⏱️  TIME'S UP! Maximum steps reached.")
            print(f"   Final score: {total_reward:.1f}")
            print(f"   Steps taken: {info['step_count']}")
            print("=" * 60)

            # Ask to continue
            choice = input("\nTry again? (y/n): ").strip().lower()
            if choice != "y":
                print("\n👋 Thanks for playing!")
                break

            episode += 1
            total_reward = 0.0
            obs, _ = env.reset()
            print("\n🔄 Starting new episode...")
            env.render()
            print_stats(episode, 0, total_reward)


def main():
    """Main entry point for playable GridWorld."""
    import argparse

    parser = argparse.ArgumentParser(description="Play GridWorld manually")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)",
    )
    args = parser.parse_args()

    try:
        play_gridworld(difficulty=args.difficulty)
    except KeyboardInterrupt:
        print("\n\n👋 Thanks for playing!")
        sys.exit(0)


if __name__ == "__main__":
    main()
