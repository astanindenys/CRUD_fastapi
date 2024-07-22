from typing import Optional
from beanie import init_beanie, PydanticObjectId
from models.hobby import Hobby, Topic, Discussion
from models.users import User
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: Optional[str]
    SECRET_KEY: Optional[str]
    
    class Config:
        env_file = ".env"
    
    async def initialize_database(self):
        client = AsyncIOMotorClient(self.DATABASE_URL)
        await init_beanie(database=client.get_default_database(), document_models=[Hobby, Topic, Discussion, User])

class Database:
    def __init__(self, model):
        self.model = model
        
    async def save(self, document):
        await document.create()
        return document
    
    async def get(self, id: PydanticObjectId):
        doc = await self.model.get(id)
        if doc:
            return doc
        return None
    
    async def get_all(self):
        docs = await self.model.find_all().to_list()
        return docs
    
    async def update(self, id: PydanticObjectId, body: BaseModel):
        des_body = body.dict()
        des_body = {k: v for k, v in des_body.items() if v is not None}
        update_query = {"$set": des_body}

        doc = await self.get(id)
        if not doc:
            return None
        await doc.update(update_query)
        return doc

    async def delete(self, id: PydanticObjectId):
        doc = await self.get(id)
        if not doc:
            return None
        await doc.delete()
        return True