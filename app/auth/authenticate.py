from datetime import timedelta
import datetime
import os
from app.auth.jwt_handler import verify_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional
from jose import jwt, JWTError
from app.models.users import User
from app.database.connection import Settings

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/securities/signin")

async def authenticate(token: Optional[str] = Depends(oauth2_scheme)) -> str:
    if not token:
        return None
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Sign in for access"
        # )

    decoded_token = verify_access_token(token)
    return decoded_token["user"]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iss": str(oauth2_scheme.tokenUrl)})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_user_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
                             , options={"verify_iss": True})
        user_id = payload.get("sub")
        if user_id is None or payload.get("iss") != str(oauth2_scheme.tokenUrl):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return User(id=user_id, username=payload.get("username"), role=payload.get("role"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")