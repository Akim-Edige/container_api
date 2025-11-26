from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_event_manager
from app.api.serializers import serialize_container
from app.crud import containers as containers_crud
from app.crud.exceptions import (
    ContainerConflictError,
    ContainerNotFoundError,
    ZoneNotFoundError,
    ZoneOverloadedError,
)
from app.database import get_session
from app.events import ContainerEventManager
from app.schemas import ContainerCreate, ContainerRead, ContainerStatusUpdate

router = APIRouter()


@router.get("", response_model=list[ContainerRead])
async def list_containers(session: AsyncSession = Depends(get_session)) -> list[ContainerRead]:
    return await containers_crud.list_containers(session)


@router.post("", response_model=ContainerRead, status_code=201)
async def create_container(
    container_in: ContainerCreate,
    session: AsyncSession = Depends(get_session),
    event_manager: ContainerEventManager = Depends(get_event_manager),
) -> ContainerRead:
    try:
        container = await containers_crud.create_container(session, container_in)
    except ZoneNotFoundError:
        raise HTTPException(status_code=404, detail="Zone not found")
    except ZoneOverloadedError:
        raise HTTPException(status_code=400, detail="Zone Overloaded")
    except ContainerConflictError:
        raise HTTPException(status_code=409, detail="Container number already exists")

    payload = {"event": "container.created", "data": serialize_container(container)}
    await event_manager.broadcast(payload)
    return container


@router.patch("/{container_id}", response_model=ContainerRead)
async def update_container_status(
    container_id: int,
    payload: ContainerStatusUpdate,
    session: AsyncSession = Depends(get_session),
    event_manager: ContainerEventManager = Depends(get_event_manager),
) -> ContainerRead:
    try:
        container = await containers_crud.update_container_status(session, container_id, payload)
    except ContainerNotFoundError:
        raise HTTPException(status_code=404, detail="Container not found")

    await event_manager.broadcast({"event": "container.updated", "data": serialize_container(container)})
    return container


