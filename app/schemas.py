from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class LoginResponse(BaseModel):
    id:int
    username:str
    email:EmailStr
    token:str
    refresh_token:str
    token_type:str

class LoginRequest(BaseModel):
    username:str
    password:str
class TokenData(BaseModel):
    user_id :str
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserCreated(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True
        exclude = ['password']  # Exclude 'password' field from the response

