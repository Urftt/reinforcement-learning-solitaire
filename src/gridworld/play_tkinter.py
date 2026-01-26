"""Interactive GridWorld game using Tkinter (native, always works on macOS!).

Tkinter comes with Python, requires zero additional dependencies,
and has excellent macOS support with proper event loop handling.
"""

import tkinter as tk
from typing import Literal

from src.gridworld.config import GridWorldConfig
from src.gridworld.environment import GridWorldEnv


class GridWorldTkinterRenderer:
    """Tkinter-based renderer for GridWorld with keyboard controls."""

    # Color scheme
    COLORS = {
        "background": "#F0F0F0",
        "grid_line": "#C8C8C8",
        "empty": "#FFFFFF",
        "agent": "#3498DB",  # Blue
        "goal": "#2ECC71",  # Green
        "obstacle": "#E74C3C",  # Red
        "trail": "#85C1E9",  # Light blue for trail
        "text": "#2C3E50",
    }

    def __init__(
        self,
        env: GridWorldEnv,
        cell_size: int = 80,
        show_trail: bool = True,
        master: tk.Tk | None = None,
    ):
        """Initialize the Tkinter renderer.

        Args:
            env: GridWorld environment to render
            cell_size: Size of each grid cell in pixels
            show_trail: Whether to show agent's movement trail
            master: Optional Tk root window
        """
        self.env = env
        self.config = env.config
        self.cell_size = cell_size
        self.show_trail = show_trail

        # Trail tracking
        self.trail: list[tuple[int, int]] = []
        self.max_trail_length = 50

        # Create window
        if master is None:
            self.root = tk.Tk()
            self.owns_root = True
        else:
            self.root = master
            self.owns_root = False

        self.root.title("GridWorld - Reinforcement Learning")

        # Calculate dimensions
        grid_width = self.config.grid_size * cell_size
        grid_height = self.config.grid_size * cell_size
        stats_height = 120

        # Create canvas for the grid
        self.canvas = tk.Canvas(
            self.root,
            width=grid_width,
            height=grid_height,
            bg=self.COLORS["background"],
            highlightthickness=0,
        )
        self.canvas.pack()

        # Create stats frame
        self.stats_frame = tk.Frame(self.root, bg="white", height=stats_height)
        self.stats_frame.pack(fill=tk.BOTH)
        self.stats_frame.pack_propagate(False)

        # Stats labels
        self.stats_label = tk.Label(
            self.stats_frame,
            text="",
            font=("Arial", 12),
            bg="white",
            fg=self.COLORS["text"],
            justify=tk.LEFT,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.stats_label.pack(fill=tk.BOTH, expand=True)

        # Keyboard bindings
        self.current_action = None
        self.root.bind("<Key>", self._on_key_press)
        self.root.bind("<Escape>", lambda e: self.root.quit())

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.running = True

    def render(
        self,
        step_count: int = 0,
        total_reward: float = 0.0,
        last_reward: float | None = None,
        episode: int = 1,
        message: str | None = None,
    ):
        """Render the current state.

        Args:
            step_count: Number of steps taken
            total_reward: Cumulative reward
            last_reward: Reward from last action
            episode: Current episode number
            message: Optional message to display
        """
        # Clear canvas
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(self.config.grid_size + 1):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(
                x,
                0,
                x,
                self.config.grid_size * self.cell_size,
                fill=self.COLORS["grid_line"],
                width=1,
            )
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(
                0,
                y,
                self.config.grid_size * self.cell_size,
                y,
                fill=self.COLORS["grid_line"],
                width=1,
            )

        # Draw trail
        if self.show_trail and self.trail:
            for i, (tx, ty) in enumerate(self.trail):
                # Fade older trail
                alpha_factor = (i + 1) / len(self.trail)
                # Tkinter doesn't support alpha, so use lighter colors for older trail
                x1 = tx * self.cell_size + 10
                y1 = ty * self.cell_size + 10
                x2 = (tx + 1) * self.cell_size - 10
                y2 = (ty + 1) * self.cell_size - 10

                # Use lighter colors for older trail segments
                if alpha_factor < 0.33:
                    color = "#D6EAF8"  # Very light blue
                elif alpha_factor < 0.66:
                    color = "#AED6F1"  # Light blue
                else:
                    color = self.COLORS["trail"]  # Trail blue

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        # Draw obstacles
        for ox, oy in self.config.obstacles:
            x1 = ox * self.cell_size + 5
            y1 = oy * self.cell_size + 5
            x2 = (ox + 1) * self.cell_size - 5
            y2 = (oy + 1) * self.cell_size - 5

            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=self.COLORS["obstacle"], outline="darkred", width=2
            )

            # Draw X
            margin = self.cell_size // 4
            self.canvas.create_line(
                ox * self.cell_size + margin,
                oy * self.cell_size + margin,
                (ox + 1) * self.cell_size - margin,
                (oy + 1) * self.cell_size - margin,
                fill="white",
                width=3,
            )
            self.canvas.create_line(
                (ox + 1) * self.cell_size - margin,
                oy * self.cell_size + margin,
                ox * self.cell_size + margin,
                (oy + 1) * self.cell_size - margin,
                fill="white",
                width=3,
            )

        # Draw goal
        gx, gy = self.config.goal_pos
        center_x = gx * self.cell_size + self.cell_size // 2
        center_y = gy * self.cell_size + self.cell_size // 2
        radius = self.cell_size // 3

        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            fill=self.COLORS["goal"],
            outline="darkgreen",
            width=2,
        )
        self.canvas.create_text(
            center_x, center_y, text="G", font=("Arial", 24, "bold"), fill="white"
        )

        # Draw agent
        if self.env.agent_pos is not None:
            ax, ay = self.env.agent_pos

            # Update trail
            if self.show_trail:
                pos_tuple = (int(ax), int(ay))
                if not self.trail or self.trail[-1] != pos_tuple:
                    self.trail.append(pos_tuple)
                    if len(self.trail) > self.max_trail_length:
                        self.trail.pop(0)

            center_x = ax * self.cell_size + self.cell_size // 2
            center_y = ay * self.cell_size + self.cell_size // 2
            radius = self.cell_size // 3

            self.canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                fill=self.COLORS["agent"],
                outline="darkblue",
                width=2,
            )
            self.canvas.create_text(
                center_x, center_y, text="A", font=("Arial", 24, "bold"), fill="white"
            )

        # Update stats with better formatting
        stats_lines = []
        stats_lines.append(
            f"Episode: {episode}    Steps: {step_count}    Total Reward: {total_reward:+.2f}"
        )

        if last_reward is not None:
            reward_indicator = "✓" if last_reward > 0 else ("✗" if last_reward < 0 else "→")
            stats_lines.append(f"Last Action: {last_reward:+.2f} {reward_indicator}")

        if message:
            stats_lines.append("")  # Blank line
            stats_lines.append(message)

        stats_lines.append("")  # Blank line
        stats_lines.append("Controls: Arrow keys / WASD = Move    R = Restart    Q/ESC = Quit")

        stats_text = "\n".join(stats_lines)
        self.stats_label.config(text=stats_text)

        # Update display
        self.root.update_idletasks()
        self.root.update()

    def _on_key_press(self, event):
        """Handle keyboard input."""
        key = event.keysym.lower()

        # Map keys to actions
        action_map = {
            "up": "up",
            "w": "up",
            "down": "down",
            "s": "down",
            "left": "left",
            "a": "left",
            "right": "right",
            "d": "right",
            "r": "restart",
            "q": "quit",
            "escape": "quit",
        }

        self.current_action = action_map.get(key)

    def _on_close(self):
        """Handle window close event."""
        self.running = False
        if self.owns_root:
            self.root.destroy()

    def clear_trail(self):
        """Clear the movement trail."""
        self.trail = []

    def close(self):
        """Close the window."""
        self.running = False
        if self.owns_root:
            self.root.destroy()

    def is_running(self):
        """Check if the window is still open."""
        return self.running

    def get_action(self):
        """Get the current action and clear it."""
        action = self.current_action
        self.current_action = None
        return action


def play_gridworld_tkinter(
    config: GridWorldConfig | None = None, difficulty: Literal["easy", "medium", "hard"] = "medium"
):
    """Interactive GridWorld game with Tkinter graphics.

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

    # Create environment and renderer
    env = GridWorldEnv(config)
    renderer = GridWorldTkinterRenderer(env, cell_size=80, show_trail=True)

    # Game state
    episode = 1
    total_reward = 0.0
    last_reward = None
    obs, _ = env.reset()
    message = f"Difficulty: {difficulty.upper()} - Use arrow keys or WASD to move!"

    print(f"\n{'=' * 60}")
    print(f"GridWorld - {difficulty.upper()} Mode (Tkinter)")
    print("=" * 60)
    print("Game window opened! Use arrow keys or WASD to move.")
    print("Press R to restart, Q or ESC to quit.")
    print("=" * 60)

    # Initial render
    renderer.render(
        step_count=0,
        total_reward=total_reward,
        last_reward=last_reward,
        episode=episode,
        message=message,
    )

    # Game state tracking
    game_over = [False]  # Use list to allow modification in nested function

    # Game loop - this properly integrates with Tkinter's event loop
    def game_step():
        """Process one game step."""
        nonlocal episode, total_reward, last_reward, obs, message

        if not renderer.is_running():
            return

        # Check for action
        action_str = renderer.get_action()

        if action_str == "quit":
            renderer.close()
            return

        if action_str == "restart":
            # Restart episode
            episode += 1
            total_reward = 0.0
            last_reward = None
            obs, _ = env.reset()
            renderer.clear_trail()
            game_over[0] = False
            message = "New episode started!"

            renderer.render(
                step_count=0,
                total_reward=total_reward,
                last_reward=last_reward,
                episode=episode,
                message=message,
            )
            # Schedule next step
            renderer.root.after(10, game_step)
            return

        # Only process movement if game is not over
        if action_str and not game_over[0]:
            action_map = {
                "up": GridWorldEnv.UP,
                "down": GridWorldEnv.DOWN,
                "left": GridWorldEnv.LEFT,
                "right": GridWorldEnv.RIGHT,
            }
            action = action_map.get(action_str)

            if action is not None:
                # Execute action
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                last_reward = reward

                # Update message based on outcome
                if terminated:
                    game_over[0] = True
                    if info["is_goal"]:
                        # Calculate efficiency
                        optimal_steps = abs(config.goal_pos[0] - config.start_pos[0]) + abs(
                            config.goal_pos[1] - config.start_pos[1]
                        )

                        if info["step_count"] == optimal_steps:
                            message = (
                                f"PERFECT! Optimal path in {info['step_count']} steps! "
                                "Press R to restart."
                            )
                        elif info["step_count"] <= optimal_steps + 3:
                            message = (
                                f"EXCELLENT! Goal in {info['step_count']} steps! "
                                f"(Optimal: {optimal_steps}) Press R."
                            )
                        else:
                            message = (
                                f"Goal reached in {info['step_count']} steps! "
                                f"(Optimal: {optimal_steps}) Press R."
                            )

                    elif info["is_obstacle"]:
                        message = (
                            f"Hit obstacle! Survived {info['step_count']} steps. "
                            "Press R to restart."
                        )

                elif truncated:
                    game_over[0] = True
                    message = "Time's up! Max steps reached. Press R to restart."
                else:
                    message = None  # Clear message during gameplay

                # Render
                renderer.render(
                    step_count=info["step_count"],
                    total_reward=total_reward,
                    last_reward=last_reward,
                    episode=episode,
                    message=message,
                )

        # Schedule next step (10ms = ~100 FPS for responsiveness)
        renderer.root.after(10, game_step)

    # Start the game loop
    game_step()

    # Run the Tkinter main loop
    try:
        renderer.root.mainloop()
    except KeyboardInterrupt:
        pass

    print("\nThanks for playing!")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Play GridWorld with Tkinter graphics!")
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)",
    )
    args = parser.parse_args()

    try:
        play_gridworld_tkinter(difficulty=args.difficulty)
    except KeyboardInterrupt:
        print("\nThanks for playing!")


if __name__ == "__main__":
    main()
