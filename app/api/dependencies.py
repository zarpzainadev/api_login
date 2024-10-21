import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.crud import crud_user
from app.schemas.user import TokenData
from app.database import get_db
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)

#security = HTTPBearer()

def get_current_user(token: str, db: Session = Depends(get_db)):
    print(f"Received token: {token[:10]}...")  
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        print("Attempting to decode JWT token")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"Decoded payload: {payload}")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            print("No user_id found in token payload")
            raise credentials_exception
        
    except JWTError as e:
        print(f"JWTError occurred: {str(e)}")
        raise credentials_exception
    
    try:
        user = crud_user.get_user(db, user_id=int(user_id))
        if user is None:
            print(f"No user found for user_id: {user_id}")
            raise credentials_exception
        print(f"User found: {user.id}")
        return user
    except Exception as e:
        print(f"Error occurred while fetching user: {str(e)}")
        raise credentials_exception
        raise credentials_exception