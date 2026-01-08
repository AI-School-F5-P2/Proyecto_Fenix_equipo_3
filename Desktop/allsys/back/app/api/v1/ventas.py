from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_session
from app.repositories.ventas_repo import registrar_venta

venta_router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)


# =========================
# REGISTRAR VENTA
# =========================
@venta_router.post("/")
def crear_venta(
    db: Session = Depends(get_session),
    variante_id: int = Form(...),
    talla_id: int = Form(...),
    cantidad: int = Form(...),
    precio_venta: float = Form(...),
    fecha: str = Form(...),        # yyyy-mm-dd
    canal: str = Form(...),        # wallapop | vinted | web
    vendedor: str = Form(...),     # maikol | paola | yenny
    comprador: str | None = Form(None),
):
    try:
        venta = registrar_venta(
            db=db,
            variante_id=variante_id,
            talla_id=talla_id,
            cantidad=cantidad,
            precio_venta=precio_venta,
            fecha=fecha,
            canal=canal,
            vendedor=vendedor,
            comprador=comprador
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "mensaje": "Venta registrada correctamente",
        "venta_id": venta.id
    }


# =========================
# CONSULTAR PRODUCTO POR TALLA
# =========================
@venta_router.get("/producto/{talla_id}")
def consultar_producto(
    talla_id: int,
    db: Session = Depends(get_session)
):
    from app.repositories.ventas_repo import obtener_producto_por_talla

    producto = obtener_producto_por_talla(db, talla_id)
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado para esa talla"
        )

    return producto
