from fastapi import WebSocket
from typing import List
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_position_update(self, position: dict):
        """Broadcast position update"""
        await self.broadcast({
            "type": "position_update",
            "data": position
        })

    async def broadcast_trade_executed(self, trade: dict):
        """Broadcast trade execution"""
        await self.broadcast({
            "type": "trade_executed",
            "data": trade
        })

    async def broadcast_system_status(self, status: dict):
        """Broadcast system status update"""
        await self.broadcast({
            "type": "system_status",
            "data": status
        })
