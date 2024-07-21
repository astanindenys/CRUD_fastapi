from fastapi import Depends, HTTPException, status
from beanie import PydanticObjectId
from fastapi.security import OAuth2PasswordBearer
from database.conection import Settings
from models.users import User, Role, UserProfileUpdate
from service.users import ALGORITHM, HashPassword, authenticate
from jose import JWTError, jwt


hash_password = HashPassword()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")
settings = Settings()


async def get_all_users():
    users = await User.find_all().to_list()
    return users

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user = await User.find_one(User.email == payload.get("user"))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

async def get_user_by_id(user_id: PydanticObjectId):
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

async def get_moderator_users():
    moderators = await User.find_all(User.role == Role.moderator).to_list()
    return moderators

async def get_admin_users():
    admins = await User.find_all(User.role == Role.admin).to_list()
    return admins


async def is_email_in_use(email: str) -> bool:
    user_with_email = await User.find_one(User.email == email)
    return user_with_email is not None

async def edit_user(user: User, current_user_email: str = Depends(authenticate)):  
    if user.email != current_user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    email_in_use = await is_email_in_use(user.email)
    if email_in_use:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    hashed_password = hash_password.create_hash(user.password)
    update_data = {
        "email": user.email,
        "password": hashed_password
    }

    await User.find_one_and_update(User.email == current_user_email, {"$set": update_data})

    return {"message": "User profile updated successfully"}


async def update_profile(user: User, profile_data: UserProfileUpdate):
    if profile_data.name:
        user.name = profile_data.name
    if profile_data.hobby:
        user.hobby = profile_data.hobby
    await user.save()
    return {"message": "Profile updated successfully"}
    

async def delete_user(user: User, current_user_email: str = Depends(authenticate)):
    if user.email != current_user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Permission denied")    
    existing_user = await User.find_one(User.email == user.email)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await existing_user.delete() 
    return {"message": "User successfully deleted"}