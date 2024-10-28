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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud_user.get_user(db, user_id=int(user_id))
    if user is None or user.rol_id != 1:  # Verificar rol_id
        raise credentials_exception
    return user
