async def edit_comment(hobby_name: str, topic_name: str, comment_id: str, comment: DiscussionCreate, current_user: User = Depends(get_current_user)):
    topic = await check_topic(hobby_name, topic_name)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    existing_comment = await Discussion.find_one(Discussion.id == comment_id)
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

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