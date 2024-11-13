from datetime import datetime
import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.crud import crud_user
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
    
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Obtener el user_id y exp del payload
        user_id: Optional[str] = payload.get("sub")
        expiration: Optional[int] = payload.get("exp")

        
        
        # Verificar que exista el user_id
        if user_id is None:
            raise credentials_exception
            
        # Verificar la expiración
        if expiration is not None:
            current_time = int(datetime.utcnow().timestamp())

            print(expiration)
            print(current_time)

            if current_time > expiration:
                raise expired_exception
                
    except JWTError:
        raise credentials_exception

    # Verificar que el usuario existe en la base de datos
    user = crud_user.get_user(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
        
    return user
