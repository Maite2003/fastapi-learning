from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from jwt.exceptions import InvalidTokenError
from . import schema
from .database import SessionDep
from . import models
from .config import get_settings

settings = get_settings()
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

oath2_scheme = OAuth2PasswordBearer(tokenUrl='login')

"""
data is the payload
"""
def create_access_token(data: dict):
    to_encode = data.copy() # So we don't change the original data
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:   
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if not id:
            raise credentials_exception
        
        token_data = schema.TokenData(id=id)
    except PyJWTError:
        raise credentials_exception
    
    return token_data

"""
Take the token from the request, verify it's correct
get the user id and fetch the user
"""    
def get_current_user(db: SessionDep ,token: str = Depends(oath2_scheme)): # type: ignore
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token =  verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user



