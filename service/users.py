import time
from datetime import datetime
from passlib.context import CryptContext
from database.conection import Settings

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from models.users import Role, User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/signin")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = Settings()
ALGORITHM = "HS256"
TOKEN_EXPIRES = 1500


def create_access_token(user: str) -> str:
    payload = {
        "user": user,
        "expires": time.time() + TOKEN_EXPIRES
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token

async def verify_access_token(token:str) -> dict:
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=ALGORITHM)
        expire = data.get("expires")
        if expire is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No access token supplied")
        if datetime.now() > datetime.fromtimestamp(expire):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")
        user_exist = await User.find_one(User.email==data["user"])
        if not user_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user found")
        return data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
    
class HashPassword:
    def create_hash(self, password:str):
        return pwd_context.hash(password)
    
    def verify_hash(self, plain_password:str, hashed_password:str):
        return pwd_context.verify(plain_password, hashed_password)
    

async def authenticate(token:str=Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Signin to get access")
    decoded_token = await verify_access_token(token)
    return decoded_token["user"]


async def promote_to_moderator(user: User, hobby_name: str):
    user.role = Role.moderator
    user.moderated_hobbies.append(hobby_name)
    await user.save()