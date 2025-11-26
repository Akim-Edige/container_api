from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import ContainerStatus


class ZoneBase(BaseModel):
    name: str
    capacity: int = Field(..., ge=0)
    type: str


class ZoneRead(ZoneBase):
    id: int
    current_load: int

    class Config:
        orm_mode = True


class ContainerBase(BaseModel):
    number: str
    type: str
    status: ContainerStatus = ContainerStatus.ARRIVED
    zone_id: Optional[int] = None
    arrival_time: Optional[datetime] = None


class ContainerCreate(ContainerBase):
    ...


class ContainerRead(ContainerBase):
    id: int
    arrival_time: datetime
    zone: Optional[ZoneRead] = None

    class Config:
        orm_mode = True


class ContainerStatusUpdate(BaseModel):
    status: ContainerStatus


class ZoneAssignRequest(BaseModel):
    container_id: int


