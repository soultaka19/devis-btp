import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import decode_token
from app.core.websocket_manager import ws_manager

router = APIRouter()


@router.websocket("/quote/{quote_id}")
async def quote_websocket(websocket: WebSocket, quote_id: int):
    # Authenticate via query param token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Token manquant")
        return

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=4001, reason="Token invalide")
        return

    user_id = int(payload["sub"])
    await ws_manager.connect(websocket, user_id, quote_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            msg_type = message.get("type")

            if msg_type == "ping":
                await ws_manager.send_to_user(user_id, quote_id, {"type": "pong"})

            elif msg_type == "update_lines":
                # Client sends updated line items, broadcast to all connections on this quote
                await ws_manager.send_to_quote(quote_id, {
                    "type": "lines_updated",
                    "data": message.get("data"),
                    "from_user": user_id,
                })

            elif msg_type == "update_field":
                await ws_manager.send_to_quote(quote_id, {
                    "type": "field_updated",
                    "data": message.get("data"),
                    "from_user": user_id,
                })

    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, quote_id)
    except Exception:
        await ws_manager.disconnect(user_id, quote_id)
