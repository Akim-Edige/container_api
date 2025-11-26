from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_event_manager
from app.api.serializers import serialize_container
from app.crud import containers as containers_crud
from app.crud import zones as zones_crud
from app.crud.exceptions import (
    ContainerNotFoundError,
    ZoneNotFoundError,
    ZoneOverloadedError,
)
from app.database import get_session
from app.events import ContainerEventManager
from app.schemas import ContainerRead, ZoneAssignRequest, ZoneRead

router = APIRouter()


@router.get("", response_model=list[ZoneRead])
async def list_zones(session: AsyncSession = Depends(get_session)) -> list[ZoneRead]:
    return await zones_crud.list_zones(session)


@router.post("/{zone_id}/assign", response_model=ContainerRead)
async def assign_container_to_zone(
    zone_id: int,
    assignment: ZoneAssignRequest,
    session: AsyncSession = Depends(get_session),
    event_manager: ContainerEventManager = Depends(get_event_manager),
) -> ContainerRead:
    try:
        container = await containers_crud.assign_container_to_zone(
            session, zone_id, assignment.container_id
        )
    except ZoneNotFoundError:
        raise HTTPException(status_code=404, detail="Zone not found")
    except ContainerNotFoundError:
        raise HTTPException(status_code=404, detail="Container not found")
    except ZoneOverloadedError:
        raise HTTPException(status_code=400, detail="Zone Overloaded")

    await event_manager.broadcast({"event": "container.assigned", "data": serialize_container(container)})
    return container


