from sqlalchemy import select
from models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:

    @staticmethod
    async def create(session: AsyncSession, user_schema) -> User:

        new_user = User(
            username=user_schema.username,
            name=user_schema.name,
            email=user_schema.email,
            hashed_password=user_schema.password
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    @staticmethod
    async def get_email(session: AsyncSession, email: str) -> User | None:

        result = await session.execute(
            select(User).where(User.email == email)
            )
        
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_username(session: AsyncSession, username: str) -> User | None:

        result = await session.execute(
            select(User).where(User.username == username)
            )
        
        return result.scalar_one_or_none()
    

    @staticmethod
    async def get_id(session: AsyncSession, user_id: int) -> User | None:

        result = await session.execute(
            select(User).where(User.id == user_id)
            )
        
        return result.scalar_one_or_none()