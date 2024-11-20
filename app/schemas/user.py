from enum import Enum
from pydantic import BaseModel, EmailStr, validator
from datetime import date, datetime
from typing import List, Optional


#Esquemas para iniciar sesion (validaciones)
class GrupoTipo(str, Enum):
    Simbolica = 'Simbolica'
    Regular = 'Regular'

class LoginRequest(BaseModel):
    grupo: GrupoTipo
    numero: str
    username: str  # Puede ser email o DNI
    password: str

    @validator('username')
    def validate_username(cls, v):
        # Validar si es un DNI válido (8 dígitos) o un email
        if v.isdigit() and len(v) == 8:
            return v
        elif '@' in v:
            return v
        raise ValueError('El username debe ser un DNI válido (8 dígitos) o un correo electrónico')

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class MessageResponse(BaseModel):
    detail: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class Token_regenerate(BaseModel):
    access_token: str
    token_type: str


# Esquema para crear una nueva sesión
class SessionCreate(BaseModel):
    usuario_id: int
    token: str
    fecha_expiracion: datetime

# Esquema para devolver una sesión
class Session(BaseModel):
    id: int
    usuario_id: int
    token: str
    fecha_expiracion: datetime

    class Config:
        orm_mode = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

#schema de respuesta para identifcador de pantalla
class ScreenGroupResponse(BaseModel):
    id: int
    name: str
    identifier: str

    class Config:
        orm_mode = True

class UsuarioScreenGroupsResponse(BaseModel):
    user_id: int
    screen_groups: List[ScreenGroupResponse]

    class Config:
        orm_mode = True


