import asyncio
import json
from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self._connections: dict[int, dict[int, WebSocket]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int, quote_id: int):
        await websocket.accept()
        async with self._lock:
            self._connections[quote_id][user_id] = websocket

    async def disconnect(self, user_id: int, quote_id: int):
        async with self._lock:
            self._connections[quote_id].pop(user_id, None)
            if not self._connections[quote_id]:
                del self._connections[quote_id]

    async def send_to_quote(self, quote_id: int, data: dict):
        conns = self._connections.get(quote_id, {})
        for ws in conns.values():
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                pass

    async def send_to_user(self, user_id: int, quote_id: int, data: dict):
        ws = self._connections.get(quote_id, {}).get(user_id)
        if ws:
            try:
                await ws.send_text(json.dumps(data))
            except Exception:
                pass


ws_manager = WebSocketManager()
