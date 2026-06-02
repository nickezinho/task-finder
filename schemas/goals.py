from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from models.enums import Priority


class GoalCreate(BaseModel):
    title: str
    description: str

    priority: Priority 
    deadline: datetime | None = None


class GoalResponse(BaseModel):
    id: int

    title: str
    description: str

    priority: Priority 
    deadline: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class GoalUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

    priority: Priority | None = None
    deadline: datetime | None = None