from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from data.hobby import create_hobby, delete_comment, delete_hobby, delete_topic, edit_comment, edit_hobby, edit_topic, list_hobbies, get_hobby, create_topic
from data.users import get_current_user
from models.hobby import Discussion, DiscussionCreate, Hobby, HobbyCreate, Topic, TopicCreate
from models.users import User
from service.users import authenticate

hobby_router = APIRouter()

@hobby_router.post("/hobby/create", response_model=Hobby)
async def new_hobby(hobby: HobbyCreate, current_user: User = Depends(authenticate)):
    return await create_hobby(hobby, current_user)

@hobby_router.get("/hobby/all", response_model=List[Hobby])
async def all_hobbies():
    return await list_hobbies()

@hobby_router.get("/hobby/{hobby_name}", response_model=Dict)
async def hobby(hobby_name: str):
    return await get_hobby(hobby_name)

@hobby_router.delete("/hobby/{hobby_name}/delete")
async def hobby_delete(hobby_name: str, current_user: User = Depends(get_current_user)):
    return await delete_hobby(hobby_name, current_user)

@hobby_router.put("/hobby/{hobby_name}/edit")
async def hobby_edit(hobby_name: str, hobby: HobbyCreate, current_user: User = Depends(get_current_user)):
    return await edit_hobby(hobby_name, hobby, current_user)

@hobby_router.post("/hobby/{hobby_name}/topic", response_model=Topic)
async def new_topic(hobby_name: str, topic: TopicCreate, current_user: User = Depends(authenticate)):
    return await create_topic(hobby_name, topic, current_user)


@hobby_router.put("/hobby/{hobby_name}/{topic_name}/edit")
async def topic_edit(hobby_name: str, topic_name: str, topic: TopicCreate, current_user: User = Depends(get_current_user)):
    return await edit_topic(hobby_name, topic_name, topic, current_user)

@hobby_router.delete("/hobby/{hobby_name}/{topic_name}")
async def topic_delete(hobby_name: str, topic_name: str, current_user: User = Depends(get_current_user)):
    return await delete_topic(hobby_name, topic_name, current_user)


@hobby_router.post("/hobby/{hobby_name}/{topic_name}/comment", response_model=Discussion)
async def comment_create(hobby_name: str, topic_name: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    return await create_comment(hobby_name, topic_name, comment, current_user)

@hobby_router.put("/hobby/{hobby_name}/{topic_name}/comment/{comment_id}", response_model=Discussion)
async def comment_edit(hobby_name: str, topic_name: str, comment_id: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    return await edit_comment(hobby_name, topic_name, comment_id, comment, current_user)


@hobby_router.delete("/hobby/{hobby_name}/{topic_name}/comment/{comment_id}", response_model=Discussion)
async def comment_edit(hobby_name: str, topic_name: str, comment_id: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    return await delete_comment(hobby_name, topic_name, comment_id, comment, current_user)