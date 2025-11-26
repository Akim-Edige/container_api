from __future__ import annotations

from typing import Any, Set

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder


class ContainerEventManager:
    """Stores active websocket connections and broadcasts container events."""

    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        serializable_payload = jsonable_encoder(payload)
        living: Set[WebSocket] = set()
        for connection in list(self._connections):
            try:
                await connection.send_json(serializable_payload)
                living.add(connection)
            except WebSocketDisconnect:
                continue
        self._connections = living


