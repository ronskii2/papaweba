from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: UUID4
    is_active: bool
    is_verified: bool
    is_admin: bool

    class Config:
        from_attributes = True
