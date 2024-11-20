from fastapi import HTTPException
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from app.models.user import EstadoCuentaUsuario, Organizacion, RoleScreenGroup, ScreenGroup, Sesion, Usuario, UsuarioOrganizacion
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from sqlalchemy.exc import NoResultFound

#funciona para verificar organizacion
def get_organization_by_grupo_numero(db: Session, grupo: str, numero: str):
    return db.query(Organizacion).filter(
        and_(
            Organizacion.grupo == grupo,
            Organizacion.numero == numero
        )
    ).first()

#funcion para verificar correo y dni
def get_user_by_username(db: Session, username: str):
    """
    Busca un usuario por email o DNI
    """
    return db.query(Usuario).filter(
        or_(
            Usuario.email == username,
            Usuario.dni == username
        )
    ).first()

#
def get_user_organization_association(db: Session, user_id: int, organization_id: int):
    return db.query(UsuarioOrganizacion).filter(
        and_(
            UsuarioOrganizacion.id_usuario == user_id,
            UsuarioOrganizacion.id_organizacion == organization_id
        )
    ).first()

def get_account_status(db: Session, user_id: int):
    return db.query(EstadoCuentaUsuario).filter(
        EstadoCuentaUsuario.id_usuario == user_id
    ).first()

def update_account_status(db: Session, account_status: EstadoCuentaUsuario, 
                         estado: str = None, 
                         intentos_fallidos: int = None,
                         fecha_bloqueo: datetime = None):
    if estado is not None:
        account_status.estado = estado
    if intentos_fallidos is not None:
        account_status.intentos_fallidos = intentos_fallidos
    if fecha_bloqueo is not None:
        account_status.fecha_bloqueo = fecha_bloqueo
    
    db.commit()
    db.refresh(account_status)
    return account_status

def verify_account_status(db: Session, account_status: EstadoCuentaUsuario):
    if account_status.estado == "Bloqueado":
        if account_status.fecha_bloqueo:
            tiempo_transcurrido = datetime.utcnow() - account_status.fecha_bloqueo
            if tiempo_transcurrido < timedelta(minutes=15):
                raise HTTPException(
                    status_code=403,
                    detail="Cuenta bloqueada temporalmente. Por favor, intente más tarde."
                )
            else:
                update_account_status(
                    db, 
                    account_status, 
                    estado="Activo",
                    intentos_fallidos=0,
                    fecha_bloqueo=None
                )


def get_user(db: Session, user_id: int):
    return db.query(Usuario).filter(Usuario.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()


#fucncion para obtener el identicador de pantalla
def get_screen_group_by_user_id(db: Session, user_id: int):
    # Buscar el usuario por su ID
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    
    if usuario is None:
        raise NoResultFound("Usuario no encontrado")

    # Obtener el role_id del usuario
    role_id = usuario.rol_id

    # Buscar los ScreenGroups asociados a ese role_id
    screen_group = db.query(ScreenGroup).join(
        RoleScreenGroup, RoleScreenGroup.screen_group_id == ScreenGroup.id
    ).filter(RoleScreenGroup.role_id == role_id).all()

    if screen_group is None:
        raise NoResultFound("No se encontraron grupos de pantalla para este rol")

    return screen_group