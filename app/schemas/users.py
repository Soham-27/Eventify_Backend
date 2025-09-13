from pydantic import BaseModel, EmailStr
import uuid
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "USER"  # Default role is 'USER'

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class UserOut(BaseModel):
    user_id: uuid.UUID
    role: str
    email: EmailStr
    token: str

    model_config = {
        "arbitrary_types_allowed": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserWithToken(UserOut):
    token: str

class UserMe(BaseModel):
    user_id: uuid.UUID
    role: str