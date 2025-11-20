from datetime import datetime, timedelta,timezone
from jose import jwt , JWTError
from passlib.context import CryptContext
from fastapi import HTTPException,Request,Depends
import os

SECRET_KEY=os.environ['SECRET_KEY']
ALGORITHM=os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES=os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to create access token. {e}")

def decode_token(request:Request):
    try:
        token = request.cookies.get("auth_token")
        if not token:
            raise HTTPException(status_code=401,detail="No authentication token provided.")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload   
    except JWTError as e:
        raise HTTPException(status_code=401,detail=f"Invalid token.")
    except Exception as e:
        raise HTTPException(status_code=401,detail=f"Failed to decode token. {e}")