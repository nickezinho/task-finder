from fastapi import HTTPException

from repositories.goal_repository import GoalRepository
from repositories.task_repository import TaskRepository


class TaskService:

    @staticmethod
    async def create_task(session, task_schema, user_id):
        new_task = await TaskRepository.create(
            session, 
            task_schema, 
            user_id
        )

        return new_task

    @staticmethod
    async def list_goal_tasks(session, goal_id, user_id):
        
        goal = await GoalRepository.get_goal_by_id(session, goal_id)

        tasks = await TaskRepository.list_tasks_by_goal(session, goal_id)

        if not tasks or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Tasks not found"
            )

        return tasks
    
    @staticmethod
    async def get_task_by_id(session, task_id, user_id):

        task = await TaskRepository.get_task_by_id(session, task_id)    

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        goal = await GoalRepository.get_goal_by_id(session, task.goal_id)

        if goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        
        return task
    

    @staticmethod
    async def update_task(session, task_id, task_update_schema, user_id):

        task = await TaskRepository.get_task_by_id(session, task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        goal = await GoalRepository.get_goal_by_id(session, task.goal_id)

        if goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        
        return await TaskRepository.update_task(session, task, task_update_schema)
    
    @staticmethod
    async def delete_task(session, task_id, user_id):

        task = await TaskRepository.get_task_by_id(session, task_id)

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        goal = await GoalRepository.get_goal_by_id(session, task.goal_id)

        if goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
            
        
        await TaskRepository.delete(task, session)

        return {
            'message':'Task deleted successfully'
        }