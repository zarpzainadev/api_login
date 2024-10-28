from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Date, Enum, DateTime, Text
from app.database import Base
from sqlalchemy.orm import relationship



class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)  

class EstadoUsuario(Base):
    __tablename__ = "estados_usuario"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    descripcion = Column(Text, nullable=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    dni = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos_paterno = Column(String(50), nullable=False)
    apellidos_materno = Column(String(50), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    celular = Column(String(20), nullable=True)
    rol_id = Column(Integer, ForeignKey("roles.id"))
    estado_id = Column(Integer, ForeignKey("estados_usuario.id"))
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    reset_token = Column(String(255), nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    rol = relationship("Rol") 
    estado = relationship("EstadoUsuario")  

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=False)

    usuario = relationship("Usuario") 
