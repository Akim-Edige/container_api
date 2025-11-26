from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Container, ContainerStatus, Zone
from app.schemas import ContainerCreate, ContainerStatusUpdate

from . import zones as zone_crud
from .exceptions import (
    ContainerConflictError,
    ContainerNotFoundError,
    ZoneNotFoundError,
    ZoneOverloadedError,
)


async def list_containers(session: AsyncSession) -> list[Container]:
    result = await session.execute(
        select(Container).options(selectinload(Container.zone)).order_by(Container.id)
    )
    return result.scalars().unique().all()


async def create_container(
    session: AsyncSession, container_in: ContainerCreate
) -> Container:
    zone: Zone | None = None
    if container_in.zone_id is not None:
        zone = await zone_crud.get_zone(session, container_in.zone_id, lock=True)
        if zone is None:
            raise ZoneNotFoundError()
        if zone.current_load >= zone.capacity:
            raise ZoneOverloadedError()

    arrival_time = container_in.arrival_time or datetime.now(timezone.utc)

    container = Container(
        number=container_in.number,
        type=container_in.type,
        status=container_in.status,
        zone=zone,
        arrival_time=arrival_time,
    )

    if zone is not None:
        zone.current_load += 1

    session.add(container)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ContainerConflictError() from exc

    await session.refresh(container, attribute_names=["zone"])
    return container


async def update_container_status(
    session: AsyncSession, container_id: int, payload: ContainerStatusUpdate
) -> Container:
    container = await _get_container(session, container_id, lock=True)
    if container is None:
        raise ContainerNotFoundError()

    previous_status = container.status
    container.status = payload.status

    if (
        previous_status != ContainerStatus.DEPARTED
        and payload.status == ContainerStatus.DEPARTED
        and container.zone is not None
    ):
        container.zone.current_load = max(container.zone.current_load - 1, 0)
        container.zone = None
        container.zone_id = None

    await session.commit()
    await session.refresh(container, attribute_names=["zone"])
    return container


async def assign_container_to_zone(
    session: AsyncSession, zone_id: int, container_id: int
) -> Container:
    zone = await zone_crud.get_zone(session, zone_id, lock=True)
    if zone is None:
        raise ZoneNotFoundError()

    container = await _get_container(session, container_id, lock=True)
    if container is None:
        raise ContainerNotFoundError()

    if container.zone_id == zone.id:
        return container

    if zone.current_load >= zone.capacity:
        raise ZoneOverloadedError()

    if container.zone is not None:
        container.zone.current_load = max(container.zone.current_load - 1, 0)

    container.zone = zone
    if container.status != ContainerStatus.DEPARTED:
        container.status = ContainerStatus.STORED
    zone.current_load += 1

    await session.commit()
    await session.refresh(container, attribute_names=["zone"])
    await session.refresh(zone)
    return container


async def _get_container(
    session: AsyncSession, container_id: int, *, lock: bool = False
) -> Container | None:
    stmt = (
        select(Container)
        .options(selectinload(Container.zone))
        .where(Container.id == container_id)
    )
    if lock:
        stmt = stmt.with_for_update()
    result = await session.execute(stmt)
    return result.scalars().unique().one_or_none()


