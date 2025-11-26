from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.events import ContainerEventManager

router = APIRouter()


@router.websocket("/ws/containers")
async def container_updates(websocket: WebSocket) -> None:
    event_manager: ContainerEventManager = websocket.app.state.event_manager
    await event_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        event_manager.disconnect(websocket)


