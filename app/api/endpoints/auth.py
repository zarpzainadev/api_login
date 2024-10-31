import logging
from fastapi import APIRouter, Depends, HTTPException, logger, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.api.email import send_email
from ...crud import crud_user
from ...schemas.user import PasswordResetConfirm, PasswordResetRequest, RefreshTokenRequest, Token_regenerate, UserCreate, Token, Session
from ...core.security import create_access_token, create_password_reset_token, get_password_hash, logout_user, verify_password, create_refresh_token, verify_reset_token
from ...database import get_db
from ...models.user import EstadoUsuario
from ...models.user import Sesion
from datetime import datetime, timedelta
from ...config import settings

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security = HTTPBearer()


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = None
    if '@' in form_data.username:
        user = crud_user.get_user_by_email(db, email=form_data.username)
    elif form_data.username.isdigit() and len(form_data.username) == 8:
        user = crud_user.get_user_by_dni(db, dni=form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(user.estado_id)

    BLOCKED_STATE_IDS = [3]

    if user.estado_id in BLOCKED_STATE_IDS:
        logger.warning(f"Blocked user attempted to login: {user.id}") ## no olvidar preguntar al ingeniero sobre a que estados se le permite iniciar sesion
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is blocked",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )

    session_expiration = datetime.utcnow() + refresh_token_expires

    db_session = Sesion(
        usuario_id=user.id,
        token=refresh_token,
        fecha_expiracion=session_expiration
    )

    db.add(db_session)
    db.commit()

    logger.info(f"User {user.id} logged in successfully")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for email: {user.email}")
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud_user.get_user_by_dni(db, dni=user.dni)
    if db_user:
        logger.warning(f"Registration attempt with existing DNI: {user.dni}")
        raise HTTPException(status_code=400, detail="DNI already registered")
    
    user = crud_user.create_user(db=db, user=user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_token_expires
    )
    
    logger.info(f"User registered successfully: {user.id}")
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
        
        return {"message": "debes de revisar el codigo"}

    token = create_password_reset_token(db, user.id)
    
    # recordar implementar el link de frontend
    reset_link = f"https://tuaplicacion.com/reset-password?token={token}"

    print(token)

    send_email(
        to_email=user.email,
        subject="Restablecimiento de Contraseña",
        body=f"haz click en el enlace para reestablecer: {reset_link}"
    )

    return {"message": "se envio conexito el correo"}


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

    return {"message": "La contraseña ha sido restablecida con éxito"}

@router.post("/logout")
def logout(
    refresh_token: str,
    db: Session = Depends(get_db),
    token: HTTPBearer = Depends(security)
):
    
    current_user = get_current_user(token.credentials, db)

    if refresh_token is None:
        raise HTTPException(status_code=400, detail="Refresh token is required")
    
    result = logout_user(refresh_token, db)

    return result
