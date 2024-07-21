from fastapi import Depends, HTTPException, status
from data.users import get_current_user
from models.hobby import Discussion, DiscussionCreate, Hobby, HobbyCreate, Topic, TopicCreate
from models.users import Role, User

async def create_hobby(hobby: HobbyCreate, current_user: User):
    existing_hobby = await Hobby.find_one(Hobby.name == hobby.name)
    if existing_hobby:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hobby already exists")
    new_hobby = Hobby(**hobby.model_dump(), owner=current_user.email)
    await new_hobby.insert()
    return new_hobby

async def list_hobbies():
    hobbies = await Hobby.find_all().to_list()
    return hobbies

async def get_hobby(hobby_name: str):
    hobby = await Hobby.find_one(Hobby.name == hobby_name)
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    topics = await Topic.find(Topic.hobby_id == hobby_name).to_list()
    return {"hobby": hobby, "topics": topics}


async def delete_hobby(hobby_name: str, current_user: User = Depends(get_current_user)):
    existing_hobby = await Hobby.find_one(Hobby.name == hobby_name)
    
    if not existing_hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    if current_user.role == Role.admin or (current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies):
        await existing_hobby.delete()
        return {"message": "Hobby deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to delete the hobby")

async def edit_hobby(hobby_name: str, hobby: HobbyCreate, current_user: User = Depends(get_current_user)):
    existing_hobby = await Hobby.find_one(Hobby.name == hobby_name)
    if not existing_hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")

    if current_user.email == existing_hobby.owner or current_user.role == Role.admin or (current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies):
        for field, value in hobby.model_dump().items():
            if value is not None:
                setattr(existing_hobby, field, value)
        await existing_hobby.save()
        return {"message": "Hobby updated successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


async def check_topic(hobby_name: str, topic_name: str):
    existing_topic = await Topic.find_one(Topic.name == topic_name)
    if not existing_topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
    if existing_topic.hobby_name != hobby_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The topic is not related to the given hobby")
    return existing_topic


async def create_topic(hobby_name: str, topic: TopicCreate, current_user: User = Depends(get_current_user)):
    hobby = await Hobby.find_one(Hobby.name == hobby_name)
    if not hobby:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hobby not found")
    
    existing_topic = await Topic.find_one({"hobby_name": hobby_name, "name": topic.name})
    if existing_topic:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Topic already exists in this hobby")

    new_topic = Topic(**topic.dict(), hobby_name=hobby_name, owner=current_user.email)
    await new_topic.insert()
    hobby.topics.append(new_topic.id)
    await hobby.save()


async def edit_topic(hobby_name: str, topic_name: str, topic: TopicCreate, current_user: User = Depends(get_current_user)):
    existing_topic = await check_topic(hobby_name, topic_name)
    
    if current_user.email == existing_topic.owner or current_user.role == Role.admin or (current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies):
        for field, value in topic.model_dump().items():
            if value is not None:
                setattr(existing_topic, field, value)
        await existing_topic.save()
        return {"message": "Topic updated successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    
async def delete_topic(hobby_name: str, topic_name: str, current_user: User = Depends(get_current_user)):
    existing_topic = await check_topic(hobby_name, topic_name)
    if current_user.email == existing_topic.owner or current_user.role == Role.admin or (current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies):
        await existing_topic.delete()
        return {"message": "Topic deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


async def create_comment(hobby_name: str, topic_name: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    topic = await check_topic(hobby_name, topic_name)
    new_comment = Discussion(**comment.model_dump(), topic_name=topic_name, owner=current_user.email)
    await new_comment.insert()
    topic.discussions.append(new_comment.id)
    await topic.save()
    return {"message": "Comment created successfully"}


async def edit_comment(hobby_name: str, topic_name: str, comment_id: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    topic = await check_topic(hobby_name, topic_name)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")
 
    existing_comment = await Discussion.find_one(Discussion.id == comment_id)
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if existing_comment.topic_name != topic_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment does not belong to the specified topic")

    if current_user.email == existing_comment.owner or current_user.role == Role.admin or (
        current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies
    ):
        
        for field, value in comment.model_dump().items():
            if value is not None:
                setattr(existing_comment, field, value)
        await existing_comment.save()
        return {"message": "Comment updated successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


async def delete_comment(hobby_name: str, topic_name: str, comment_id: str, current_user: User = Depends(get_current_user)):
    topic = await check_topic(hobby_name, topic_name)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    existing_comment = await Discussion.find_one(Discussion.id == comment_id)
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if current_user.email == existing_comment.owner or current_user.role == Role.admin or (
        current_user.role == Role.moderator and hobby_name in current_user.moderated_hobbies
    ):
        await existing_comment.delete()
        return {"message": "Comment deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")