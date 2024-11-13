import secrets
from fastapi import Depends, HTTPException, logger, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import models
from app.config import settings
from app.schemas.user import Session
from app.models.user import Sesion , Usuario
from sqlalchemy.orm import Session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Convertir el datetime a timestamp (segundos desde epoch)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # default 7 días
    
    # Convertir el datetime a timestamp (segundos desde epoch)
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



def logout_user(refresh_token: str, db: Session):
    try:
        # Busca la sesión asociada al refresh token
        session = db.query(Sesion).filter(Sesion.token == refresh_token).first()
        
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        
        # Elimina solo la sesión actual
        db.delete(session)
        db.commit()
        return {"message": "Successfully logged out from this device"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error during logout for refresh token {refresh_token}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred during logout: {str(e)}")




#Funciones para recuperar la contraseña

def create_password_reset_token(db: Session, user_id: int):
    # Generar un token seguro
    token = f"{user_id}_{secrets.token_urlsafe(32)}"
    expiration = datetime.utcnow() + timedelta(hours=1)

   
    user = db.query(Usuario).filter(Usuario.id == user_id).first()  
    if user:
        user.reset_token = token
        user.reset_token_expiry = expiration
        db.commit()
        return token
    
    
    return None

def verify_reset_token(db: Session, token: str):
    try:
        
        user_id = int(token.split('_')[0]) 
        
       
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if user:
            
            if user.reset_token == token and user.reset_token_expiry > datetime.utcnow():
                return user  
    except (ValueError, IndexError):
        
        pass
    
    return None
