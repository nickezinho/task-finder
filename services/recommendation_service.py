from fastapi import HTTPException
from repositories.goal_repository import GoalRepository 
from repositories.task_repository import TaskRepository
from clients.gemini_client import GeminiClient
from schemas.tasks import TaskCreate
from models.enums import Status
from utils.prompts import generate_recommendation_prompt, generate_recommended_task
import json
import re


def _extract_json_payload(response_text: str):
    """Extract JSON even when the model wraps it with markdown or extra text."""
    if not response_text:
        raise json.JSONDecodeError("Empty response", response_text, 0)

    cleaned = response_text.strip()

    # Try plain JSON first.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Remove optional markdown fences.
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Fallback: extract first JSON object/array from text.
    array_match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if array_match:
        return json.loads(array_match.group(0))

    obj_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if obj_match:
        return json.loads(obj_match.group(0))

    raise json.JSONDecodeError("No JSON payload found", cleaned, 0)

class RecommendationService:

    @staticmethod
    async def generate_recommendation(session, goal_id, user_id):
        gemini = GeminiClient()

        goal = await GoalRepository.get_goal_by_id(session, goal_id)

        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        prompt = generate_recommendation_prompt(goal.title, goal.description)

        response = gemini.generate_content(prompt)

        if not response:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate recommendation"
            )
        
        try:
            tasks_data = _extract_json_payload(response)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid response format from recommendation service"
            )
        
        created_tasks = []

        for task_data in tasks_data:

            task_schema = TaskCreate(
                goal_id=goal_id,
                **task_data)
            
            task = await TaskRepository.create(
                session,
                task_schema)
            
            created_tasks.append(task)


        return created_tasks
    
    @staticmethod
    async def recommend_task(session, goal_id, user_id):

        gemini = GeminiClient()

        goal = await GoalRepository.get_goal_by_id(session, goal_id)

        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        tasks = await TaskRepository.list_tasks_by_goal(session, goal_id)

        if not tasks:
            raise HTTPException(
                status_code=404,
                detail="No tasks found for this goal"
            )
        
        tasks_for_ai = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "difficulty": task.difficulty.value,
                "estimated_minutes": task.estimated_minutes,
                "status": task.status.value
            }
            for task in tasks
            if task.status != Status.COMPLETED
        ]

        if not tasks_for_ai:
            raise HTTPException(
                status_code=400,
                detail="No pending tasks available for recommendation"
            )
     
        tasks_json = json.dumps(
            tasks_for_ai,
            ensure_ascii=False,
            indent=2
        )

        prompt = generate_recommended_task(
            goal.title,
            goal.description,
            goal.priority.value,
            goal.deadline,
            tasks_json
        )

        response = gemini.recommend_task(prompt)

        if not response:
            raise HTTPException(
                status_code=400,
                detail="Failed to generate recommendation"
            )   
        
        try:
            task_data = _extract_json_payload(response)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid response format from recommendation service"
            )

        if not isinstance(task_data, dict) or "task_id" not in task_data or "reason" not in task_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid recommendation payload"
            )

        try:
            task_id = int(task_data["task_id"])
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="Invalid task_id in recommendation payload"
            )
        
        recommended_task = await TaskRepository.get_task_by_id(
            session,
            task_id
        )

        if not recommended_task or recommended_task.goal_id != goal_id:
            raise HTTPException(
                status_code=400,
                detail="Recommended task is invalid for this goal"
            )

        return {
            "task": recommended_task,
            "reason": str(task_data["reason"]).strip()
        }

    
        

        
