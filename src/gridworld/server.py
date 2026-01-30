"""FastAPI server for GridWorld training interface.

Provides WebSocket endpoint for real-time training communication
and serves static frontend files.
"""

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles


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

    Accepts connections, processes incoming commands, and maintains
    connection lifecycle. Commands will be handled by training loop
    in Plan 03.

    Args:
        websocket: WebSocket connection from client
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Log received message (full implementation in Plan 03)
            msg_type = data.get("type", "unknown")
            print(f"Received message: {msg_type}")

            # Echo acknowledgment for now
            await websocket.send_json({
                "type": "ack",
                "message": f"Received {msg_type}"
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")


# Mount static files (will be created in Plan 02)
# This serves index.html, app.js, styles.css from static/ directory
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except RuntimeError:
    # Static directory doesn't exist yet - will be created in Plan 02
    print("Static directory not found - will be created in Plan 02")
