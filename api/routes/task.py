from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from schemas.tasks import TaskResponse, TaskUpdate, TaskCreate
from services.task_service import TaskService
from ..deps import get_current_user, get_db

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

@task_router.post("/create/", response_model=TaskResponse)
async def create_task(
    task_schema: TaskCreate,
    db: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to create a new task."""
    try:
        result = await TaskService.create_task(db, task_schema, current_user.id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@task_router.get("/from-goal/{goal_id}", response_model=list[TaskResponse])
async def list_goal_tasks(
    goal_id: int,
    db: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to list all tasks of the current user."""
    try:
        result = await TaskService.list_goal_tasks(db,  goal_id, current_user.id)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int,
    db: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to get a specific task by its ID."""
    try:
        result = await TaskService.get_task_by_id(db, task_id, current_user.id)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@task_router.patch("/{task_id}")
async def update_task(
    task_id: int,
    task_update_schema: TaskUpdate,
    session: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Endpoint to update a task."""
    try:
        result = await TaskService.update_task(session, task_id, task_update_schema, current_user.id)
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@task_router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    session: AsyncSession=Depends(get_db),
    current_user = Depends(get_current_user)    
):
    """Endpoint to delete a task."""
    try:
        await TaskService.delete_task(session, task_id, current_user.id)
        return {"detail": "Task deleted successfully"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
