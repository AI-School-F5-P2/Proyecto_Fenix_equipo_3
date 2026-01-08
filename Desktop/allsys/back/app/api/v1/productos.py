import json
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, HTTPException, UploadFile, Query
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.api.deps import get_current_admin
from app.repositories.producto_repo import (
    crear_producto,
    editar_producto_completo,
    obtener_producto_completo,
    obtener_productos_paginados,
    editar_variante,
    # agregar_imagenes_variante,
    # eliminar_imagen_variante,
    
    eliminar_producto
)

producto_routers = APIRouter(prefix="/productos", tags=["Productos"])


# ================= CREAR PRODUCTO =================
@producto_routers.post("/")
def crear_producto_endpoint(
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),

    # Datos básicos
    nombre: str = Form(...),
    descripcion: str = Form(...),
    tipo: str = Form(...),
    precio: float = Form(...),
    categoria_id: int = Form(...),
    marca_id: int = Form(...),

    # 🆕 Datos de compra
    lugar_compra: Optional[str] = Form(None),
    fecha_compra: Optional[str] = Form(None),  # yyyy-mm-dd
    precio_compra: Optional[float] = Form(None),

    # Variantes e imágenes
    variantes: str = Form(...),  # JSON string
    imagenes: Optional[List[UploadFile]] = File(None)
):
    producto = crear_producto(
        db=db,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        marca_id=marca_id,
        tipo=tipo,

        # 🆕 pasar datos de compra
        lugar_compra=lugar_compra,
        fecha_compra=fecha_compra,
        precio_compra=precio_compra,

        variantes=variantes,
        imagenes=imagenes
    )

    return {
        "mensaje": "Producto creado correctamente",
        "producto_id": producto.id
    }


# ================= OBTENER PRODUCTO =================
@producto_routers.get("/{producto_id}")
def obtener_producto(producto_id: int, db: Session = Depends(get_session)):
    producto = obtener_producto_completo(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


# ================= LISTAR PRODUCTOS =================
@producto_routers.get("/")
def listar_productos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_session),
):
    return obtener_productos_paginados(db, page, limit)


# ================= EDITAR PRODUCTO =================
from fastapi import UploadFile, File

@producto_routers.put("/{producto_id}")
def editar_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),

    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    categoria_id: Optional[int] = Form(None),
    marca_id: Optional[int] = Form(None),
    tipo: Optional[str] = Form(None),

    # 🆕 DATOS DE COMPRA
    lugar_compra: Optional[str] = Form(None),
    fecha_compra: Optional[str] = Form(None),
    precio_compra: Optional[float] = Form(None),

    variantes: Optional[str] = Form(None),
    imagenes: Optional[List[UploadFile]] = File(None)
):
    producto = editar_producto_completo(
        db=db,
        producto_id=producto_id,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        marca_id=marca_id,
        tipo=tipo,
        lugar_compra=lugar_compra,
        fecha_compra=fecha_compra,
        precio_compra=precio_compra,
        variantes=variantes,
        imagenes=imagenes
    )

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"mensaje": "Producto actualizado correctamente"}




# ================= EDITAR VARIANTE =================
@producto_routers.put("/variantes/{variante_id}")
def editar_variante_endpoint(
    variante_id: int,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),
    color: Optional[str] = Form(None),
    color_nombre: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    descuento: Optional[float] = Form(None),
    tallas: Optional[str] = Form(None),  # JSON string: [{"id":1,"stock":10},...]
):
    tallas_list = json.loads(tallas) if tallas else None
    variante = editar_variante(
        db=db,
        variante_id=variante_id,
        color=color,
        color_nombre=color_nombre,
        precio=precio,
        descuento=descuento,
        tallas=tallas_list
    )
    if not variante:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
    return {"mensaje": "Variante actualizada correctamente"}



@producto_routers.delete("/{producto_id}")
def eliminar_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin)
    
):
    eliminado = eliminar_producto(db, producto_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {"message": "Producto eliminado correctamente"}