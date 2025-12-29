from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import crear_token_acceso, verificar_password
from app.db.database import get_session
from app.models.usuario_model import Usuario
from app.schemas.usuarios_schema import UsuarioCreate, UsuarioOut
from app.services.usuarios_services import crear_usuario
from app.schemas.usuarios_schema import LoginRequest, TokenResponse


auth_routers = APIRouter(prefix="/auth", tags=["Autenticación"])

# ✅ Registro
@auth_routers.post("/register", response_model=UsuarioOut)
def register(usuario_in: UsuarioCreate, db: Session = Depends(get_session)):
    nuevo_usuario = crear_usuario(db, usuario_in)
    return nuevo_usuario


@auth_routers.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_session)):
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if not verificar_password(login_data.password, usuario.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")

    token = crear_token_acceso({"sub": usuario.email, "id": usuario.id})

    return {"access_token": token, "token_type": "bearer"}