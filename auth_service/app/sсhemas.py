from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    # email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    username: str
    # email: Optional[EmailStr] = None

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True
