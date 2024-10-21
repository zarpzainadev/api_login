from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from datetime import datetime

def get_user_by_dni(db: Session, dni: str):
    return db.query(User).filter(User.dni == dni).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = User(
        dni=user.dni,
        email=user.email,
        password_hash=get_password_hash(user.password),
        nombre=user.nombre,
        apellidos=user.apellidos,
        fecha_nacimiento=user.fecha_nacimiento,
        celular=user.celular,
        rol=user.rol,
        estado=user.estado,
        fecha_registro=datetime.utcnow(),
        reset_token=None,
        reset_token_expiry=None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
