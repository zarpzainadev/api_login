from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

# Esquema base de usuario
class UserBase(BaseModel):
    dni: str
    email: EmailStr
    nombres: str
    apellidos_paterno: str
    apellidos_materno: str
    fecha_nacimiento: date
    celular: str
    rol_id: int 
    estado_id: int
    

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    password_hash: str
    fecha_registro: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    login: str  
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class Token_regenerate(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

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