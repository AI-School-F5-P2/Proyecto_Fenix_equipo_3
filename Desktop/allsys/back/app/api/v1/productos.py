from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.api.deps import get_current_admin
from app.repositories.producto_repo import crear_producto, obtener_producto_completo, obtener_productos_paginados

producto_routers = APIRouter(prefix="/productos", tags=["Productos"])

@producto_routers.post("/")
def crear_producto_endpoint(
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    tipo: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...),
    marca_id: int = Form(...),
    variantes: str = Form(...),  # JSON string
    imagenes: Optional[List[UploadFile]] = File(None)  # opcional
):

    # return
    producto = crear_producto(
        db=db,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        marca_id=marca_id,
        variantes=variantes,
        imagenes=imagenes,
        tipo=tipo
    )
    return {"mensaje": "Producto creado correctamente", "producto_id": producto.id}






@producto_routers.get("/{producto_id}")
def obtener_producto(producto_id: int, db: Session = Depends(get_session)):
    producto = obtener_producto_completo(db, producto_id)

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return producto



@producto_routers.get("/")
def listar_productos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_session),
):
    return obtener_productos_paginados(db, page, limit)