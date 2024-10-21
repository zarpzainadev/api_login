import secrets
from fastapi import Depends, HTTPException, logger
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import models
from app.config import settings
from app.schemas.user import Session
from app.models.user import Session as Sesion, User
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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



def logout_user(current_user: User, db: Session):
    try:
        sessions = db.query(Sesion).filter(Sesion.usuario_id == current_user.id).all()
        for session in sessions:
            db.delete(session)
        db.commit()
        return {"message": "Successfully logged out"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error during logout for user {current_user.id}: {str(e)}")
        raise



#Funciones para recuperar la contraseña

def create_password_reset_token(db: Session, user_id: int):
    # Generar un token seguro
    token = f"{user_id}_{secrets.token_urlsafe(32)}"
    expiration = datetime.utcnow() + timedelta(hours=1)

    # Actualizar el usuario en la base de datos
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.reset_token = token
        user.reset_token_expiry = expiration
        db.commit()
        return token
    return None

def verify_reset_token(db: Session, token: str):
    try:
        user_id = int(token.split('_')[0])
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.reset_token == token and user.reset_token_expiry > datetime.utcnow():
            return user
    except (ValueError, IndexError):
        pass
    return None
