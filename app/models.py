from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ContainerStatus(str, enum.Enum):
    ARRIVED = "arrived"
    STORED = "stored"
    DEPARTED = "departed"


class Container(Base):
    __tablename__ = "containers"
    __table_args__ = (UniqueConstraint("number", name="uq_container_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[ContainerStatus] = mapped_column(
        Enum(ContainerStatus), nullable=False, default=ContainerStatus.ARRIVED
    )
    zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("zones.id", ondelete="SET NULL"), nullable=True
    )
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    zone: Mapped["Zone"] = relationship(back_populates="containers")


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_load: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    type: Mapped[str] = mapped_column(String(64), nullable=False)

    containers: Mapped[list[Container]] = relationship(back_populates="zone")


