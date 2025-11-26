from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Zone


async def get_zone(
    session: AsyncSession, zone_id: int, *, lock: bool = False
) -> Zone | None:
    stmt = select(Zone).where(Zone.id == zone_id)
    if lock:
        stmt = stmt.with_for_update()
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_zones(session: AsyncSession) -> list[Zone]:
    result = await session.execute(select(Zone).order_by(Zone.id))
    return result.scalars().all()


