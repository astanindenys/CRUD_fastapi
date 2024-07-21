from service.users import HashPassword, authenticate, create_access_token, promote_to_moderator
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from models.users import User, TokenResponse, Role, UserProfileUpdate
from data.users import edit_user, get_current_user, update_profile, get_all_users, get_user_by_id, delete_user, get_admin_users, get_moderator_users
from database.conection import Database


user_router = APIRouter(tags=["User"])

user_database = Database(User)
hash_password = HashPassword()

@user_router.post("/signup")
async def sign_user_up(user:User) -> dict:
    user_exist = await User.find_one(User.email == user.email)
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already inuse")
    hashed_password = hash_password.create_hash(user.password)
    user.password = hashed_password
    user.role = Role.user
    await user_database.save(user)
    return {"message": "User successfully created"}

@user_router.put("assign-role/{user_id}")
async def assign_role(user_id: PydanticObjectId, role: Role, current_user_email:str=Depends(authenticate)):
    current_user = await User.find_one(User.email == current_user_email)
    if current_user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission")
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    user.role = role
    await user.save()
    return {"message": f"Role for {user.email} updated to {role}"}

@user_router.post("/signin", response_model=TokenResponse) 
async def sign_user_in(user:OAuth2PasswordRequestForm=Depends()) -> dict:
    user_exist = await User.find_one(User.email == user.username)
    if not user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if hash_password.verify_hash(user.password, user_exist.password):
        access_token = create_access_token(user_exist.email)
        return {"access_token": access_token, "token_type": "Bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password")

@user_router.put("/users/me/profile")
async def modify_profile(user: User, current_user_email: str = Depends(authenticate)):
    return await edit_user(user, current_user_email)


@user_router.put("/users/me/profile")
async def modify_profile(profile_data: UserProfileUpdate, current_user_email: str = Depends(authenticate)):
    user = await User.find_one(User.email == current_user_email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await update_profile(user, profile_data)

@user_router.get("/users", response_model=List[User])
async def list_users():
    users = await get_all_users()
    return users

@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id:PydanticObjectId):
    user = await get_user_by_id(user_id)
    return user

@user_router.get("/admin-users", response_model=List[User])
async def list_admin_users(current_user:User=Depends(get_admin_users)):
    return await get_admin_users()

@user_router.get("/moderator-users", response_model=List[User])
async def list_moderator_users(current_user:User=Depends(get_moderator_users)):
    return await get_moderator_users()


@user_router.delete("/users/me")
async def delete_user_by_email(current_user_email: str = Depends(authenticate)):
    user = User(email=current_user_email)
    return await delete_user(user, current_user_email=current_user_email)


@user_router.post("/user/{user_email}/promote")
async def promote_user(user_email: str, hobby_name: str, current_user: User = Depends(get_current_user)):  
    if current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Only admins can promote users")

    user_to_promote = await User.find_one(User.email == user_email)
    if not user_to_promote:
        raise HTTPException(status_code=404, detail="User not found")

    await promote_to_moderator(user_to_promote, hobby_name)

    return {"message": f"User {user_email} has been promoted to moderator of {hobby_name}"}
