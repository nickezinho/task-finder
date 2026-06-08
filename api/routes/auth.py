from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from schemas.users import LoginSchema, UserCreate, UserResponse, RegisterResponse
from services.auth_service import AuthService

from services.auth_service import AuthService

from ..deps import get_db
from core.security import limiter
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/")
async def home():
    """Endpoint for user login."""
    return {"message": "login endpoint"}


@auth_router.post("/register", response_model=RegisterResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: UserCreate, 
    db: AsyncSession=Depends(get_db),
) -> dict:
    
    """Registration endpoint for new users."""

    try:
        result = await AuthService.register_user(db, user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@auth_router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_schema: LoginSchema, 
    db: AsyncSession=Depends(get_db) 
) -> dict:
    
    """Login endpoint for existing users."""

    try:
        result = await AuthService.login(login_schema, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

#This endpoint is mostly for testing purposes, as the OAuth2PasswordRequestForm is designed to work with form data, not JSON payloads.
@auth_router.post("/login-form")
@limiter.limit("10/minute")
async def login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession=Depends(get_db)
) -> dict:
    
    """Login endpoint for form data."""
    
    login_schema = LoginSchema(username=form_data.username, password=form_data.password)
    return await AuthService.login(
        login_schema,
        db
    )

@auth_router.post("/refresh")
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    refresh_token: str
) -> dict:
    
    """Reresh access token endpoint."""
    
    try:
        result = await AuthService.use_refresh_token(refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@auth_router.get("/me", response_model=UserResponse)
async def me(
    token: str, 
    db: AsyncSession=Depends(get_db) 
) -> UserResponse:
    
    """Endpoint to get current user info."""
    
    try:
        user = await AuthService.get_current_user(token, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )