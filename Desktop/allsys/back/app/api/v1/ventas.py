from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_session
from app.schemas.ventas_schema import VentaCreate
from app.repositories import ventas_repo

venta_router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)

# =====================================================
# 💰 REGISTRAR VENTA (OMNICANAL)
# =====================================================
@venta_router.post("/")
def crear_venta(
    data: VentaCreate, 
    db: Session = Depends(get_session)
):
    """
    Registra una venta nueva, resta stock de los artículos 
    y genera snapshots históricos de los productos vendidos.
    """
    try:
        # El repositorio ahora se encarga de toda la lógica pesada
        venta = ventas_repo.registrar_venta(db, data)
        
        return {
            "success": True,
            "mensaje": "Venta registrada correctamente",
            "venta_id": venta.id,
            "codigo": venta.codigo_venta,
            "total": venta.total
        }
    except HTTPException as e:
        # Re-lanzamos errores de stock insuficiente o no encontrado
        raise e
    except Exception as e:
        # Error genérico del servidor
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# =====================================================
# 🔍 CONSULTAR STOCK PARA VENTA
# =====================================================
@venta_router.get("/producto/{stock_id}")
def consultar_producto_para_venta(
    stock_id: int,
    db: Session = Depends(get_session)
):
    """
    Endpoint rápido para que Yenny o Maikol escaneen un ID 
    y vean si hay stock antes de añadirlo al carrito.
    """
    # Reutilizamos tu lógica de obtener detalle de stock
    from app.repositories.producto_repo import obtener_stock_detalle
    
    producto = obtener_stock_detalle(db, stock_id)
    
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="El artículo no existe en el inventario"
        )

    # Verificamos si tiene stock disponible
    if producto["stock_disponible"] <= 0:
        return {
            "alerta": "⚠️ ARTÍCULO AGOTADO",
            "producto": producto
        }

    return producto