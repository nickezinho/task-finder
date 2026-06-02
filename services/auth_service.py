from datetime import timedelta

from core.security import verify_password, hash_password, create_token, verify_token
from repositories.user_repository import UserRepository

class AuthService:

    @staticmethod
    async def register_user(session, user_schema):

        new_user_schema = user_schema.model_copy()

        new_user_schema.password = hash_password(new_user_schema.password)

        existing_email = await UserRepository.get_email(session, user_schema.email)

        existing_username = await UserRepository.get_username(session, user_schema.username)

        if existing_email:
            raise ValueError("Email already registered")
        
        if existing_username:
            raise ValueError("Username already taken")
        
        new_user = await UserRepository.create(session, new_user_schema)

        return {
            "message": "User registered successfully",
            "user": new_user
        }


    @staticmethod
    async def auth_user(session, user_schema):

        user = await UserRepository.get_username(session, user_schema.username)

        if not user:
            raise ValueError("Invalid username or password")
        
        if not verify_password(user_schema.password, user.hashed_password):
            raise ValueError("Invalid username or password")
        
        return user
    

    @staticmethod
    async def login(login_schema, session):

        user = await AuthService.auth_user(session, login_schema)

        access_token = create_token(user.id, token_type="access")
        refresh_token = create_token(user.id, token_type="refresh", token_duration=timedelta(days=7))

        return {
            'refresh_token': refresh_token,
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    

    @staticmethod
    async def use_refresh_token(refresh_token):

        try:
            payload = verify_token(refresh_token, expected_type="refresh")
            
            user_id = int(payload.get("sub"))
            
            new_access_token = create_token(user_id, token_type="access")

            return {
                'access_token': new_access_token,
                'token_type': 'Bearer'
            }
        
        except Exception as e:
            raise ValueError("Invalid refresh token") from e


    @staticmethod
    async def get_current_user(token, session):

        payload = verify_token(token, expected_type="access")

        user_id = int(payload.get("sub"))

        if not user_id:
            raise ValueError("Invalid token: missing subject")
        
        user = await UserRepository.get_id(session, user_id)

        if not user:
            raise ValueError("User not found")
        
        return user