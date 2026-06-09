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


@auth_router.post(
    "/register", 
    response_model=RegisterResponse,
    summary="Register a new user",
    description="""
    Creates a new user account.

    Rate limit: 5 requests per minute.

    Requirements:
    - `username`: Unique username for the user.
    - 'email': Valid email address.
    - 'password': Strong password for the account.
    """,
    responses={
        200: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "User registered successfully",
                        "user": {
                            "id": 1,
                            "username": "johndoe",
                            "name": "John Doe",
                            "email": "johndoe@example.com"
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Invalid input data",
        },
        429: {
            "description": "Too Many Requests - Rate limit exceeded",
        }
    }
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user: UserCreate, 
    db: AsyncSession=Depends(get_db),
) -> dict:
    
    """Registration endpoint to create a new user."""

    try:
        result = await AuthService.register_user(db, user)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    

@auth_router.post(
        "/login",
        summary="User login",
        description="""
        Authenticates a user and returns access and refresh tokens.
        Rate limit: 10 requests per minute.
        Requirements:
        - `username`: The username of the user.
        - `password`: The password of the user.
        """,
        responses={
            200: {
                "description": "User logged in successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "refresh_token": "dfghjkl1234567890qwertyuiopasdfghjklzxcvbnm"
                        }
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid username or password",
            },
            429: {
                "description": "Too Many Requests - Rate limit exceeded",
            }
        }
)
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

@auth_router.post(
        "/refresh",
        summary="Refresh access token",
        description="""
        Refreshes the access token using a valid refresh token.
        Rate limit: 20 requests per minute.
        Requirements:
        - `refresh_token`: The refresh token issued during login.
        """,
        responses={
            200: {
                "description": "Access token refreshed successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                            "type": "bearer"
                        }
                    }
                }
            },
            400: {
                "description": "Bad Request - Invalid refresh token",
            },
            429: {
                "description": "Too Many Requests - Rate limit exceeded",
            }
        }
)
@limiter.limit("20/minute")
async def refresh(
    request: Request,
    refresh_token: str
) -> dict:
    
    """Refresh access token endpoint."""
    
    try:
        result = await AuthService.use_refresh_token(refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@auth_router.get(
        "/me", 
        response_model=UserResponse,
        summary="Get current user info",
        description="""
        Retrieves information about the currently authenticated user.
        Rate limit: 10 requests per minute.
        Requirements
        - `token`: A valid access token must be provided in the Authorization header.
        """,
        responses={
            200: {
                "description": "Current user information retrieved successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": 1,
                            "username": "johndoe",
                            "name": "John Doe",
                            "email": "john@doe.com",
                            "is_active": True,
                            "is_superuser": False
                        }
                    }
                }
            },
            401: {
                "description": "Unauthorized - Invalid or missing token",
            },
            429: {
                "description": "Too Many Requests - Rate limit exceeded",
            }
        }
)
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