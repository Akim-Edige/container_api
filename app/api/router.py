from fastapi import APIRouter

from .routes import containers, websocket, zones

api_router = APIRouter()
api_router.include_router(containers.router, prefix="/containers", tags=["containers"])
api_router.include_router(zones.router, prefix="/zones", tags=["zones"])

ws_router = APIRouter()
ws_router.include_router(websocket.router)


