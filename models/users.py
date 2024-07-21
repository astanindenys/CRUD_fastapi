
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import Document


class Role(str, Enum):
    admin = "admin"
    moderator = "moderator"
    user = "user"

class User(Document):
    email: EmailStr
    password: str
    name: str = Field(default="")
    hobby: List[str] = []
    role: Role = Role.user 
    moderated_hobbies: List[str] = []

    class Settings:
        collection = "users"
        
    class Config:
        json_shema_extra ={
            "example": {
                "email": "user@email.korn",
                "password": "enter_some_pass"
            }
        }
   

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    hobby: Optional[str] = None
    
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str