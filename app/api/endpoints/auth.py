import logging
from fastapi import APIRouter, Depends, HTTPException, logger, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.api.email import send_email
from ...crud import crud_user
from ...schemas.user import LoginRequest, PasswordResetConfirm, PasswordResetRequest, RefreshTokenRequest, Token_regenerate,Token, Session
from ...core.security import create_access_token, create_password_reset_token, get_password_hash, logout_user, verify_password, create_refresh_token, verify_reset_token
from ...database import get_db
from ...models.user import EstadoUsuario
from ...models.user import Sesion
from datetime import datetime, timedelta
from ...config import settings

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

security = HTTPBearer()


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    
    
    # 1. Buscar organización
    organization = crud_user.get_organization_by_grupo_numero(db, login_data.grupo, login_data.numero)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organización no encontrada"
        )
    
    # 2. Buscar usuario y verificar asociación con organización
    user = crud_user.get_user_by_username(db, login_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_org = crud_user.get_user_organization_association(db, user.id, organization.id)
    if not user_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no pertenece a esta organización"
        )
    
    # 3. Verificar estado de la cuenta
    account_status = crud_user.get_account_status(db, user.id)
    crud_user.verify_account_status(db, account_status)
    
    # 4. Validar contraseña
    if not verify_password(login_data.password, user.password_hash):
        account_status.intentos_fallidos += 1
        if account_status.intentos_fallidos >= 5:
            crud_user.update_account_status(
                db,
                account_status,
                estado="Bloqueado",
                intentos_fallidos=account_status.intentos_fallidos,
                fecha_bloqueo=datetime.utcnow()
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta bloqueada por múltiples intentos fallidos"
            )
        
        crud_user.update_account_status(
            db,
            account_status,
            intentos_fallidos=account_status.intentos_fallidos
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 5. Login exitoso
    crud_user.update_account_status(db, account_status, intentos_fallidos=0)
    
    # Generar tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    # Desactivar sesiones anteriores activas
    db.query(Sesion).filter(
        Sesion.usuario_id == user.id,
        Sesion.is_active == True
    ).update({"is_active": False})
    
    # Crear nueva sesión
    db_session = Sesion(
        usuario_id=user.id,
        token=refresh_token,
        fecha_expiracion=datetime.utcnow() + refresh_token_expires,
        is_active=True
    )
    db.add(db_session)
    db.commit()

    logger.info(f"User {user.id} logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }





@router.post("/token/refresh", response_model=Token_regenerate)
def refresh_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    logger.info("Token refresh attempt")
    session = db.query(Sesion).filter(Sesion.token == refresh_request.refresh_token).first()

    if not session:
        logger.warning("Invalid refresh token attempt")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

   
    current_time = datetime.utcnow().replace(tzinfo=None)
    session_expiration = session.fecha_expiracion.replace(tzinfo=None)

    if session_expiration < current_time:
        logger.warning(f"Expired refresh token for user: {session.usuario_id}")
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(session.usuario_id)}, expires_delta=access_token_expires  
    )

    logger.info(f"Token refreshed successfully for user: {session.usuario_id}")
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, email=request.email)
    if not user:
        
        return {"status_code": "404", "message": "El correo no existe"}

    token = create_password_reset_token(db, user.id)
    
    # recordar implementar el link de frontend
    reset_link = f"https://tuaplicacion.com/reset-password?token={token}"

    print(token)

    send_email(
        to_email=user.email,
        subject="Restablecimiento de Contraseña",
        body=f"haz click en el enlace para reestablecer: {reset_link}"
    )

    return {"status_code": "200", "message": "Se envió con éxito el correo"}


@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = verify_reset_token(db, request.token)
    if not user:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    # Actualizar la contraseña del usuario
    user.password_hash = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return {"status_code": "200", "message": "la contraseña ha sido cambiado con exito"}


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    token: HTTPBearer = Depends(security)
):
    
    current_user = get_current_user(token.credentials, db)

    session = db.query(Sesion).filter(
        Sesion.usuario_id == current_user.id,
        Sesion.is_active == True
    ).first()
    
    
    if session:
        session.is_active = False
        db.commit()
    else :
        raise HTTPException(status_code=400, detail="No active session found to logout.")


    return {"message": "Logout successful"}
