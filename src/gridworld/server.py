"""FastAPI server for GridWorld training interface.

Provides WebSocket endpoint for real-time training communication
and serves static frontend files.
"""

import asyncio
import json
import time
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

from src.gridworld.agent import QLearningAgent
from src.gridworld.config import GridWorldConfig, QLearningConfig
from src.gridworld.environment import GridWorldEnv


class ConnectionManager:
    """Manages active WebSocket connections.

    Handles connection lifecycle and message broadcasting to all connected clients.
    Supports multiple concurrent clients for future extensibility.
    """

    def __init__(self):
        """Initialize connection manager with empty connection list."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from active list.

        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        """Send message to all connected clients.

        Args:
            message: Dictionary to send as JSON to all clients
        """
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                # Client disconnected; will be cleaned up on next receive attempt
                pass


# Global connection manager instance
manager = ConnectionManager()

# Global training task reference (for start/stop control)
training_task: asyncio.Task | None = None

# Global agent reference (for Q-table save/load)
current_agent: QLearningAgent | None = None


async def training_loop(env_config: dict, agent_config: dict, num_episodes: int):
    """Async training loop that runs Q-learning with time-based state broadcasting.

    Implements non-blocking training loop following RESEARCH.md Pattern 2.
    Broadcasts training updates every 100ms (time-based) for guaranteed 10 Hz
    visualization update rate.

    Args:
        env_config: Environment configuration dict
        agent_config: Agent configuration dict with learning_rate, epsilon, discount_factor
        num_episodes: Number of training episodes to run
    """
    global current_agent

    try:
        # Create environment and agent
        grid_config = GridWorldConfig(
            grid_size=5,
            start_pos=(0, 0),
            goal_pos=(4, 4),
            obstacles=[(1, 1), (2, 2), (3, 1)],
        )
        env = GridWorldEnv(config=grid_config)

        # Create agent with user-configured parameters
        q_config = QLearningConfig(
            learning_rate=agent_config.get("learning_rate", 0.1),
            discount_factor=agent_config.get("discount_factor", 0.99),
            epsilon_start=agent_config.get("epsilon", 1.0),
            epsilon_end=0.01,
            epsilon_decay=0.995,
            num_episodes=num_episodes,
        )
        agent = QLearningAgent(config=q_config, grid_size=grid_config.grid_size)
        current_agent = agent  # Store for Q-table persistence

        # Training loop
        last_broadcast_time = time.time()
        max_steps = 100

        for episode in range(num_episodes):
            # Reset environment
            obs, info = env.reset()
            state = tuple(obs)
            step = 0
            done = False

            # Broadcast at episode start to ensure updates happen
            await manager.broadcast({
                "type": "training_update",
                "data": {
                    "episode": episode + 1,
                    "step": step,
                    "agent_pos": [int(x) for x in obs],  # Convert numpy types to Python int
                    "epsilon": float(agent.epsilon),
                },
            })
            last_broadcast_time = time.time()

            while not done and step < max_steps:
                # Agent selects action
                action = agent.select_action(state)

                # Environment step
                next_obs, reward, terminated, truncated, info = env.step(action)
                next_state = tuple(next_obs)
                done = terminated or truncated

                # Agent updates Q-table
                agent.update(state, action, reward, next_state, done)

                # Move to next state
                state = next_state
                step += 1

                # Time-based broadcasting (VIZ-04): every 100ms
                current_time = time.time()
                if (current_time - last_broadcast_time) >= 0.1:
                    await manager.broadcast({
                        "type": "training_update",
                        "data": {
                            "episode": episode + 1,
                            "step": step,
                            "agent_pos": [int(x) for x in next_obs],  # Convert numpy types to Python int
                            "epsilon": float(agent.epsilon),
                        },
                    })
                    last_broadcast_time = current_time

            # After episode: decay epsilon
            agent.decay_epsilon()

            # Yield to event loop to prevent blocking
            await asyncio.sleep(0)

        # Training complete
        await manager.broadcast({
            "type": "training_complete",
            "data": {
                "total_episodes": num_episodes,
                "final_epsilon": float(agent.epsilon),
            },
        })

    except asyncio.CancelledError:
        # Training stopped by user
        await manager.broadcast({
            "type": "training_stopped",
            "data": {"message": "Training stopped by user"},
        })
        raise

    except Exception as e:
        # Error during training
        await manager.broadcast({
            "type": "error",
            "data": {"message": f"Training error: {str(e)}"},
        })
        raise


# Create FastAPI application
app = FastAPI(title="GridWorld RL Training Server")


@app.get("/health")
async def health_check():
    """Health check endpoint for server status.

    Returns:
        dict: Status information including active connection count
    """
    return {
        "status": "ok",
        "active_connections": len(manager.active_connections),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time training communication.

    Handles commands:
    - start_training: Start async training loop
    - stop_training: Cancel running training
    - reset: Reset environment state
    - save_qtable: Persist Q-table to disk
    - load_qtable: Load Q-table from disk
    - ping: Connection health check

    Args:
        websocket: WebSocket connection from client
    """
    global training_task, current_agent

    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            msg_type = data.get("type", "unknown")
            payload = data.get("data", {})

            # Handle commands
            if msg_type == "start_training":
                # Cancel existing training if running
                if training_task and not training_task.done():
                    training_task.cancel()
                    try:
                        await training_task
                    except asyncio.CancelledError:
                        pass

                # Extract parameters from payload
                learning_rate = payload.get("learning_rate", 0.1)
                epsilon = payload.get("epsilon", 1.0)
                discount_factor = payload.get("discount_factor", 0.99)
                num_episodes = payload.get("num_episodes", 100)

                # Start new training task
                training_task = asyncio.create_task(
                    training_loop(
                        env_config={},
                        agent_config={
                            "learning_rate": learning_rate,
                            "epsilon": epsilon,
                            "discount_factor": discount_factor,
                        },
                        num_episodes=num_episodes,
                    )
                )

                await websocket.send_json({
                    "type": "training_started",
                    "data": {"num_episodes": num_episodes},
                })

            elif msg_type == "stop_training":
                if training_task and not training_task.done():
                    training_task.cancel()
                    try:
                        await training_task
                    except asyncio.CancelledError:
                        pass

                await websocket.send_json({
                    "type": "training_stopped",
                    "data": {"message": "Training stopped"},
                })

            elif msg_type == "reset":
                # Cancel training if running
                if training_task and not training_task.done():
                    training_task.cancel()
                    try:
                        await training_task
                    except asyncio.CancelledError:
                        pass

                # Reset agent
                current_agent = None

                await manager.broadcast({
                    "type": "reset_complete",
                    "data": {"message": "Environment reset"},
                })

            elif msg_type == "save_qtable":
                if current_agent:
                    try:
                        filepath = ".qtables/agent_latest.json"
                        current_agent.save_q_table(filepath)
                        await websocket.send_json({
                            "type": "save_complete",
                            "data": {
                                "success": True,
                                "filepath": filepath,
                                "message": "Q-table saved",
                            },
                        })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": f"Save failed: {str(e)}"},
                        })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "No agent to save"},
                    })

            elif msg_type == "load_qtable":
                if current_agent:
                    try:
                        filepath = ".qtables/agent_latest.json"
                        success = current_agent.load_q_table(filepath)
                        if success:
                            await websocket.send_json({
                                "type": "load_complete",
                                "data": {
                                    "success": True,
                                    "message": "Q-table loaded",
                                    "epsilon": float(current_agent.epsilon),
                                },
                            })
                        else:
                            await websocket.send_json({
                                "type": "error",
                                "data": {"message": "Q-table file not found"},
                            })
                    except Exception as e:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": f"Load failed: {str(e)}"},
                        })
                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"message": "No agent initialized"},
                    })

            elif msg_type == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "data": {"timestamp": time.time()},
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Unknown command: {msg_type}"},
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Mount static files (will be created in Plan 02)
# This serves index.html, app.js, styles.css from static/ directory
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    # Static directory doesn't exist yet - will be created in Plan 02
    print("Static directory not found - will be created in Plan 02")
