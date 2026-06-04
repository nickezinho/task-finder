from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.enums import Priority, Difficulty, Status


class TaskCreate(BaseModel):
    goal_id: int 

    title: str
    description: str | None = None
    
    estimated_minutes: int | None = None

    difficulty: Difficulty = Difficulty.MEDIUM
    

class TaskResponse(BaseModel):
    id: int

    goal_id: int 

    title: str
    description: str | None = None

    estimated_minutes: int | None = None

    difficulty: Difficulty

    status: Status

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskUpdate(BaseModel):
    status: Status 


class TaskRecommendationResponse(BaseModel):
    task: TaskResponse
    reason: str
    