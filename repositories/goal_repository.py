from sqlalchemy import select
from models.tasks import Goal
from sqlalchemy.ext.asyncio import AsyncSession


class GoalRepository:

    @staticmethod
    async def create(session: AsyncSession, goal_schema, user_id: int) -> Goal:

        new_goal = Goal(
            title=goal_schema.title,
            description=goal_schema.description,
            priority=goal_schema.priority,
            user_id=user_id
        )

        session.add(new_goal)
        await session.commit()
        await session.refresh(new_goal)
        return new_goal
    
    @staticmethod
    async def get_goal_by_id(session: AsyncSession, goal_id: int) -> Goal | None:

        result = await session.execute(
            select(Goal).where(Goal.id == goal_id)
            )
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_goals_by_user_id(session: AsyncSession, user_id: int) -> list[Goal]:

        result = await session.execute(
            select(Goal).where(Goal.user_id == user_id)
            )
        
        return result.scalars().all()
    
    @staticmethod
    async def delete(goal: Goal, session: AsyncSession):

        await session.delete(goal)
        await session.commit()

    @staticmethod
    async def update_goal(session: AsyncSession, goal: Goal, goal_update_schema) -> Goal:

        update_data = goal_update_schema.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(goal, key, value)

        await session.commit()
        await session.refresh(goal)

        return goal