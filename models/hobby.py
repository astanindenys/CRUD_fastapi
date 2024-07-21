# models/hobby.py

from pydantic import BaseModel, Field
from typing import List
from beanie import Document
from datetime import datetime

class Hobby(Document):
    name: str = Field(unique=True)
    description: str = Field(default="")
    owner: str
    
    class Settings:
        collection = "hobbies"
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Hiking",
                "description": "A group for hiking enthusiasts."
            }
        }
        
        
class HobbyCreate(BaseModel):
    name: str
    description: str = Field(default="")
    

class Topic(Document):
    name: str
    description: str = Field(default="")
    hobby_name: str  
    owner: str
    
    class Settings:
        collection = "topics"

    class Config:
        schema_extra = {
            "example": {
                "name": "Best Hiking Trails",
                "description": "Discuss the best hiking trails around the world.",
                "hobby_id": "hiking"
            }
        }
    
class TopicCreate(BaseModel):
    name: str
    description: str = Field(default="")
    hobby_name: str  
    

class Discussion(Document):
    comment: str
    topic_name: str  
    owner: str  
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
            collection = "discussions"

    class Config:
            
        schema_extra = {
            "example": {
                "comment": "Looking for trail recommendations in the Pacific Northwest.",
                "topic_name": "best-hiking-trails",
                "user_id": "user@example.com"
            }
        }



class DiscussionCreate(BaseModel):

    comment: str
    topic_name: str
