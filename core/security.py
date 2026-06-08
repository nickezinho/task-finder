from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv
load_dotenv()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
limiter = Limiter(key_func=get_remote_address)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(id_user: int, token_type: str, token_duration=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    expire = datetime.utcnow() + token_duration
    to_encode = {"sub": str(id_user), "type": token_type, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, expected_type: str):

    try: 
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        token_type: str = payload.get("type")

        if token_type != expected_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise JWTError("Invalid token")
    
