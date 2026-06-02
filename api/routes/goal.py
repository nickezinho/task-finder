from fastapi import APIRouter, Depends, HTTPException

from core.security import verify_token
from ..deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.goal_service import GoalService
from schemas.goals import GoalCreate, GoalResponse, GoalUpdate


goal_router = APIRouter(prefix="/goals", tags=["goals"])


@goal_router.post("/create", response_model=GoalResponse)
async def create_goal(goal_schema: GoalCreate,
                        db: AsyncSession=Depends(get_db),
                        current_user = Depends(get_current_user)
                    ) -> dict:
    
    """Endpoint to create a new goal."""

    try:
        result = await GoalService.create_goal(db, goal_schema, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@goal_router.get("/my-goals", response_model=list[GoalResponse])
async def list_my_goals(
    db: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
) -> list[GoalResponse]:
    """Endpoint to list all goals of the current user."""
    try:
        result = await GoalService.list_user_goals(db, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@goal_router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal_by_id(
    goal_id: int,
    db: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
) -> GoalResponse:
    """Endpoint to get a specific goal by its ID."""
    try:
        result = await GoalService.get_goal_by_id(db, goal_id, current_user.id)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@goal_router.patch("/{goal_id}")
async def update_goal(
    goal_id: int,
    goal_update_schema: GoalUpdate,
    session: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to update a specific goal by its ID."""
    try:
        result = await GoalService.update_goal(session, goal_id, goal_update_schema, current_user.id)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@goal_router.delete("/{goal_id}")
async def delete_goal(
    goal_id: int,
    session: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to delete a specific goal by its ID."""
    try:
        await GoalService.delete_goal(session, goal_id, current_user.id)
        return {"detail": "Goal deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )