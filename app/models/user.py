from datetime import datetime
import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, LargeBinary, String, Date, Enum, DateTime, Text
from app.database import Base
from sqlalchemy.orm import relationship

class GrupoTipo(enum.Enum):
    Simbolica = 'Simbolica'
    Regular = 'Regular'
    Filosófica = 'Filosófica'

class EstadoTipo(enum.Enum):
    Activo = 'Activo'
    Inactivo = 'Inactivo'

class EstadoCuentaTipo(enum.Enum):
    Bloqueado = 'Bloqueado'
    Activo = 'Activo'

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
    is_active = Column(Boolean, default=True)

    usuario = relationship("Usuario") 


class Organizacion(Base):
    __tablename__ = 'organizacion'

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    numero = Column(String(50), nullable=False)
    grupo = Column(Enum(GrupoTipo), nullable=False)
    estado = Column(Enum(EstadoTipo), nullable=False, default=EstadoTipo.Activo)

   

class UsuarioOrganizacion(Base):
    __tablename__ = 'usuario_organizacion'

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    id_organizacion = Column(Integer, ForeignKey('organizacion.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(Enum(EstadoTipo), nullable=False, default=EstadoTipo.Activo)

    
class EstadoCuentaUsuario(Base):
    __tablename__ = 'estado_cuenta_usuario'

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    estado = Column(Enum(EstadoCuentaTipo), nullable=False, default=EstadoCuentaTipo.Activo)
    fecha_bloqueo = Column(DateTime, nullable=True)
    intentos_fallidos = Column(Integer, default=0)

class ScreenGroup(Base):
    __tablename__ = 'screen_groups'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    identifier = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)


class RoleScreenGroup(Base):
    __tablename__ = 'role_screen_group'

    role_id = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    screen_group_id = Column(Integer, ForeignKey('screen_groups.id'), primary_key=True)

