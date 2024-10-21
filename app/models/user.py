from sqlalchemy import Column, Integer, LargeBinary, String, Date, Enum, DateTime
from app.database import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    member = "member"
    secretario ="secretario"
    tesorero = "tesorero"
    

class UserStatus(enum.Enum):
    Activo = "Activo"
    Ensueños = "En sueños"
    Irradiado ="Irradiado"

class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    nombre = Column(String)
    apellidos = Column(String)
    fecha_nacimiento = Column(Date)
    celular = Column(String)
    rol = Column(Enum(UserRole))
    estado = Column(Enum(UserStatus))
    fecha_registro = Column(DateTime)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)
    foto = Column(LargeBinary)
    foto_tipo_mime = Column(String(100))

class Session(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer)
    token = Column(String, unique=True, index=True)
    fecha_expiracion = Column(DateTime)