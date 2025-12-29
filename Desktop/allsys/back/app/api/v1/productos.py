from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.api.deps import get_current_admin
from app.repositories.producto_repo import crear_producto

producto_routers = APIRouter(prefix="/productos", tags=["Productos"])

@producto_routers.post("/")
def crear_producto_endpoint(
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...),
    marca_id: int = Form(...),
    variantes: str = Form(...),  # JSON string
    imagenes: Optional[List[UploadFile]] = File(None)  # opcional
):
    producto = crear_producto(
        db=db,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        marca_id=marca_id,
        variantes=variantes,
        imagenes=imagenes
    )
    return {"mensaje": "Producto creado correctamente", "producto_id": producto.id}
