from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_session
from app.schemas.ventas_schema import VentaCreate, VentaUpdate
from app.repositories import ventas_repo
from app.repositories.producto_repo import obtener_stock_detalle

venta_router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)

# =====================================================
# 1. RUTAS RAÍZ ( / )
# =====================================================

@venta_router.post("/")
def crear_venta(
    data: VentaCreate, 
    db: Session = Depends(get_session)
):
    """Registra una venta nueva y resta stock."""
    try:
        venta = ventas_repo.registrar_venta(db, data)
        return {
            "success": True,
            "mensaje": "Venta registrada correctamente",
            "venta_id": venta.id,
            "codigo": venta.codigo_venta,
            "total": venta.total
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@venta_router.get("/")
def listar_ventas(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    estado: Optional[str] = None,
    canal: Optional[str] = None,
    fecha_inicio: Optional[str] = None, # 👈 NUEVO
    fecha_fin: Optional[str] = None,
    vendedor: Optional[str] = None,   # 👈 NUEVO
    comprador: Optional[str] = None,  # 👈 NUEVO
    db: Session = Depends(get_session)
):
    """Obtiene el historial de ventas paginado y filtrado."""
    try:
        resultados = ventas_repo.obtener_ventas_paginadas(
            db=db, 
            page=page, 
            limit=limit, 
            search=search, 
            estado_venta=estado, 
            canal=canal,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            vendedor=vendedor, comprador=comprador
        )
        return resultados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {str(e)}")

# =====================================================
# 2. RUTAS ESTÁTICAS CON PARÁMETROS ( /prefijo/{id} )
# =====================================================

@venta_router.get("/producto/{stock_id}")
def consultar_producto_para_venta(
    stock_id: int,
    db: Session = Depends(get_session)
):
    """Endpoint rápido para escanear un ID y ver stock."""
    producto = obtener_stock_detalle(db, stock_id)
    
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="El artículo no existe en el inventario"
        )

    if producto["stock_disponible"] <= 0:
        return {
            "alerta": "⚠️ ARTÍCULO AGOTADO",
            "producto": producto
        }

    return producto

@venta_router.get("/detalle/{venta_id}")
def obtener_detalle_venta(venta_id: int, db: Session = Depends(get_session)):
    """Obtiene toda la información de una venta específica."""
    venta = ventas_repo.obtener_venta_por_id(db, venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

# =====================================================
# 3. RUTAS TOTALMENTE DINÁMICAS ( /{id} ) - Siempre al final
# =====================================================

@venta_router.put("/{venta_id}")
def editar_venta(venta_id: int, data: VentaUpdate, db: Session = Depends(get_session)):
    """Actualiza metadatos y estados de una venta existente."""
    try:
        venta_actualizada = ventas_repo.actualizar_venta(db, venta_id, data.dict(exclude_unset=True))
        return {"success": True, "mensaje": "Venta actualizada correctamente."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")