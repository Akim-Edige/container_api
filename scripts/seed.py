from __future__ import annotations

import asyncio

from sqlalchemy import func, select

from app.database import Base, async_session_factory, engine
from app.models import Container, ContainerStatus, Zone


SAMPLE_ZONES = [
    {"name": "North Bay", "capacity": 50, "type": "refrigerated"},
    {"name": "East Yard", "capacity": 80, "type": "dry"},
    {"name": "Hazmat Stack", "capacity": 20, "type": "hazardous"},
    {"name": "Overflow Check", "capacity": 1, "type": "dry"},
]

SAMPLE_CONTAINERS = [
    {
        "number": "CNT-0001",
        "type": "40ft",
        "status": ContainerStatus.STORED,
        "zone_name": "North Bay",
    },
    {
        "number": "CNT-0002",
        "type": "20ft",
        "status": ContainerStatus.STORED,
        "zone_name": "North Bay",
    },
    {
        "number": "CNT-0003",
        "type": "tank",
        "status": ContainerStatus.STORED,
        "zone_name": "Hazmat Stack",
    },
    {
        "number": "CNT-OVERFLOW",
        "type": "20ft",
        "status": ContainerStatus.STORED,
        "zone_name": "Overflow Check",
    },
    {
        "number": "CNT-ARRIVAL",
        "type": "45ft",
        "status": ContainerStatus.ARRIVED,
        "zone_name": None,
    },
]


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        zone_count = await session.scalar(select(func.count()).select_from(Zone))
        if zone_count and zone_count > 0:
            print("Seed data already present; skipping.")
            return

        zones_by_name: dict[str, Zone] = {}
        for payload in SAMPLE_ZONES:
            zone = Zone(**payload, current_load=0)
            session.add(zone)
            zones_by_name[payload["name"]] = zone

        await session.flush()

        for payload in SAMPLE_CONTAINERS:
            zone = zones_by_name.get(payload["zone_name"]) if payload["zone_name"] else None
            container = Container(
                number=payload["number"],
                type=payload["type"],
                status=payload["status"],
                zone=zone,
            )
            session.add(container)
            if zone:
                zone.current_load += 1

        await session.commit()
        print("Seed data inserted.")


if __name__ == "__main__":
    asyncio.run(seed())


