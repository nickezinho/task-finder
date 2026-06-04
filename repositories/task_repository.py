from sqlalchemy import select
from models.tasks import Task
from sqlalchemy.ext.asyncio import AsyncSession




class TaskRepository:

    @staticmethod
    async def create(session: AsyncSession, task_schema) -> Task:

        new_task = Task(
            title=task_schema.title,
            description=task_schema.description,
            estimated_minutes=task_schema.estimated_minutes,
            difficulty=task_schema.difficulty,
            goal_id=task_schema.goal_id
        )

        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        return new_task
    
    @staticmethod
    async def get_task_by_id(session: AsyncSession, task_id: int) -> Task | None:

        result = await session.execute(
            select(Task).where(Task.id == task_id)
            )
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_tasks_by_goal(session: AsyncSession, goal_id: int) -> list[Task]:

        result = await session.execute(
            select(Task).where(Task.goal_id == goal_id)
        )
        
        return result.scalars().all()
    

    @staticmethod
    async def update_task(session: AsyncSession, task: Task, task_update_schema) -> Task:

        update_data = task_update_schema.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(task, key, value)

        await session.commit()
        await session.refresh(task)

        return task
    

    @staticmethod 
    async def delete(task: Task, session: AsyncSession):

        await session.delete(task)
        await session.commit()