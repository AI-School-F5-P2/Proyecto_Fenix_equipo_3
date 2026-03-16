from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session

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

    stock_variante_id: int = Form(...),
    cantidad: int = Form(...),

    canal: str = Form(...),        # wallapop | vinted | web
    vendedor: str = Form(...),     # maikol | paola | yenny
    comprador: str | None = Form(None),
):
    try:
        venta = registrar_venta(
            db=db,
            stock_variante_id=stock_variante_id,
            cantidad=cantidad,
            canal=canal,
            vendedor=vendedor,
            comprador=comprador
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "mensaje": "Venta registrada correctamente",
        "venta_id": venta.id,
        "total": venta.total
    }





@venta_router.get("/producto/{stock_variante_id}")
def consultar_producto(
    stock_variante_id: int,
    db: Session = Depends(get_session)
):
    from app.repositories.ventas_repo import obtener_producto_por_stock

    producto = obtener_producto_por_stock(db, stock_variante_id)
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado para ese stock"
        )

    return producto
