from core.database import SessionLocal
from services.auth_service import AuthService
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db():
    async with SessionLocal() as db:
        yield db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login-form"
)

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db)
    ) -> dict:
    

    return await AuthService.get_current_user(
        token, 
        session
    )
