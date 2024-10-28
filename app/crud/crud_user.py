from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import Sesion, Usuario
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from datetime import datetime

def get_user_by_dni(db: Session, dni: str):
    return db.query(Usuario).filter(Usuario.dni == dni).first()

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_user(db: Session, user: UserCreate):
    db_user = Usuario(
        dni=user.dni,
        email=user.email,
        password_hash=get_password_hash(user.password),
        nombres=user.nombres,
        apellidos_paterno=user.apellidos_paterno,
        apellidos_materno=user.apellidos_materno,
        fecha_nacimiento=user.fecha_nacimiento,
        celular=user.celular,
        rol_id=user.rol_id,
        estado_id=user.estado_id,
        fecha_registro=datetime.utcnow(),
        reset_token=None,
        reset_token_expiry=None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()


