from fastapi import HTTPException

from repositories.goal_repository import GoalRepository


class GoalService:

    @staticmethod
    async def create_goal(session, 
                          goal_schema, 
                          user_id
                        ):

        new_goal = await GoalRepository.create(
            session, 
            goal_schema, 
            user_id
        )

        return new_goal

    @staticmethod
    async def list_user_goals(session, user_id):

        goals = await GoalRepository.get_goals_by_user_id(session, user_id)

        return goals

    @staticmethod
    async def get_goal_by_id(session, goal_id, user_id):

        goal = await GoalRepository.get_goal_by_id(session, goal_id)    

        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        return goal

    
    @staticmethod
    async def update_goal(session, goal_id, goal_update_schema, user_id):
        goal = await GoalRepository.get_goal_by_id(session, goal_id)

        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )

        return await GoalRepository.update_goal(session, goal, goal_update_schema)
    

    @staticmethod
    async def delete_goal(session, goal_id, user_id):
        goal = await GoalRepository.get_goal_by_id(session, goal_id)

        if not goal or goal.user_id != user_id:
            raise HTTPException(
                status_code=404,
                detail="Goal not found"
            )
        
        await GoalRepository.delete(goal, session)