from fastapi import APIRouter, Depends, HTTPException, Request

from core.security import verify_token, limiter
from ..deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.goal_service import GoalService
from schemas.goals import GoalCreate, GoalResponse, GoalUpdate


goal_router = APIRouter(prefix="/goals", tags=["goals"])


@goal_router.post(
        "/create", 
        response_model=GoalResponse,
        summary="Create a new goal",
        description="""
        Creates a new goal for the authenticated user.
        Rate limit: 5 requests per minute.
        Requirements:
        - `title`: A string representing the title of the goal (required).
        - `description`: A string providing a detailed description of the goal (optional).
        - `priority`: An enum value indicating the priority level of the goal (required).
        - `deadline`: A datetime value representing the deadline for achieving the goal (optional).
        """,
        responses={
            200: {
                "description": "Goal created successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "title": "Learn FastAPI",
                            "description": "Complete the FastAPI tutorial and build a project",
                            "priority": "HIGH",
                            "deadline": "2024-12-31T23:59:59",
                            "created_at": "2024-06-01T12:00:00" 
                            }
                        }
                    }
                },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid input data"
                        }
                    }
                }
            }
        }
)
@limiter.limit("5/minute")
async def create_goal(
    request: Request,
    goal_schema: GoalCreate,
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


@goal_router.get(
        "/my-goals", 
        response_model=list[GoalResponse],
        summary="List all goals of the current user",
        description="""
        Retrieves a list of all goals associated with the authenticated user.
        Rate limit: 5 requests per minute.
        """,
        responses={
            200: {
                "description": "List of user's goals retrieved successfully",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": 1,
                                "title": "Learn FastAPI",
                                "description": "Complete the FastAPI tutorial and build a project",
                                "priority": "HIGH",
                                "deadline": "2024-12-31T23:59:59",
                                "created_at": "2024-06-01T12:00:00" 
                            },
                            {
                                "id": 2,
                                "title": "Read a book",
                                "description": "Read 'The Pragmatic Programmer'",
                                "priority": "MEDIUM",
                                "deadline": 'null',
                                "created_at": "2024-06-02T15:30:00" 
                            }
                        ]
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid input data"
                        }
                    }
                }
            }
        }        
)
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


@goal_router.get(
        "/{goal_id}", 
        response_model=GoalResponse,
        summary="Get a specific goal by ID",
        description="""
        Retrieves a specific goal by its ID for the authenticated user.
        Rate limit: 5 requests per minute.
        Requirements:
        - `goal_id`: The ID of the goal to retrieve (required).
        """,
        responses={
            200: {
                "description": "Goal retrieved successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "title": "Learn FastAPI",
                            "description": "Complete the FastAPI tutorial and build a project",
                            "priority": "HIGH",
                            "deadline": "2024-12-31T23:59:59",
                            "created_at": "2024-06-01T12:00:00" 
                        }
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid input data"
                        }
                    }
                }
            },
            404: {
                "description": "Not Found - Goal does not exist",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Goal not found"
                        }
                    }
                }
            }
        }
)
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


@goal_router.patch(
        "/{goal_id}",
        response_model=GoalResponse,
        summary="Update a specific goal by ID",
        description="""
        Updates a specific goal by its ID for the authenticated user.
        Rate limit: 5 requests per minute.
        Requirements:
        - `goal_id`: The ID of the goal to update (required).
        - `title`: A string representing the new title of the goal (optional).
        - `description`: A string providing a new detailed description of the goal (optional).
        - `priority`: An enum value indicating the new priority level of the goal (optional).
        - `deadline`: A datetime value representing the new deadline for achieving the goal (optional).
        """,
        responses={
            200: {
                "description": "Goal updated successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "title": "Learn FastAPI and Docker",
                            "description": "Complete the FastAPI tutorial, build a project, and learn Docker",
                            "priority": "HIGH",
                            "deadline": "2024-12-31T23:59:59",
                            "created_at": "2024-06-01T12:00:00" 
                        }
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid input data"
                        }
                    }
                }
            },
            404: {
                "description": "Not Found - Goal does not exist",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Goal not found"
                        }
                    }
                }
            }
        }        
)
@limiter.limit("5/minute")
async def update_goal(
    request: Request,
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
    

@goal_router.delete(
        "/{goal_id}",
        summary="Delete a specific goal by ID",
        description="""
        Deletes a specific goal by its ID for the authenticated user.
        Rate limit: 5 requests per minute.
        Requirements:
        - `goal_id`: The ID of the goal to delete (required).
        """,
        responses={
            200: {
                "description": "Goal deleted successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Goal deleted successfully"
                        }
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid input data",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid input data"
                        }
                    }
                }
            },
            404: {
                "description": "Not Found - Goal does not exist",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Goal not found"
                        }
                    }
                }
            }
        }        
)
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