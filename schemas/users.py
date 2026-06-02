from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    name: str
    email: EmailStr
    password: str

    model_config = ConfigDict(
        from_attributes=True
    )


class UserResponse(BaseModel):
    id: int

    username: str
    name: str
    email: EmailStr

    is_active: bool
    is_superuser: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse

    model_config = ConfigDict(
        from_attributes=True
    )


class LoginSchema(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        from_attributes=True
    )
