import json
import traceback
from typing import List, Optional, Dict

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    Request,
    status
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_session
from app.api.deps import get_current_admin
from app.repositories.producto_repo import (
    crear_producto,
    destruir_producto_total,
    destruir_stock_total,
    destruir_variante_total,
    editar_producto_completo,
    mover_producto_papelera,
    mover_stock_papelera,
    mover_variante_papelera,
    obtener_producto_completo,
    obtener_productos_paginados,
    obtener_productos_papelera,
    obtener_stock_detalle,
    obtener_stocks_individuales_paginados,
    restaurar_producto_papelera,
    restaurar_stock_papelera,
    restaurar_variante_papelera,
    actualizar_stock_individual
)
from app.schemas.producto_schema import (
    PaginatedProductosResponse, 
    PaginatedStockResponse
)
from app.schemas.stock_schema import StockEditPayload

# Esquema para la edición rápida de stock
# class StockEditPayload(BaseModel):
#     cantidad: int
#     precio_compra: float
#     precio_venta: float
#     descuento: float = 0
#     ubicacion: Optional[str] = ""
#     proveedor_id: Optional[int] = None
#     proveedor_nombre_nuevo: Optional[str] = None
#     publicar_web: bool = False
#     publicar_vinted: bool = False
#     publicar_wallapop: bool = False

producto_routers = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# =====================================================
# 🔍 RUTAS DE LECTURA (GET)
# =====================================================

@producto_routers.get("/papelera")
def listar_papelera_endpoint(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin)
):
    """Lista productos en la papelera."""
    return obtener_productos_papelera(db, page=page, limit=limit)

@producto_routers.get("/inventario-individual", response_model=PaginatedStockResponse)
def listar_inventario_individual_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    tipo_busqueda: str = Query("stock_id"),
    categoria_id: Optional[int] = Query(None),
    marca_id: Optional[int] = Query(None),
    color: Optional[str] = Query(None),
    talla: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    precio_min: Optional[float] = Query(None),
    precio_max: Optional[float] = Query(None),
    solo_vendidos: bool = Query(False),
    ordenar_por: str = Query("fecha_desc"),
    proveedores_ids: List[int] = Query(default=[]),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    disponibilidad: Optional[str] = Query("todos"),
    db: Session = Depends(get_session)
):
    """Vista aplanada para gestión de inventario."""
    return obtener_stocks_individuales_paginados(
        db=db, page=page, limit=limit, search=search, 
        tipo_busqueda=tipo_busqueda, categoria_id=categoria_id,
        marca_id=marca_id, color=color, talla=talla, estado=estado,
        precio_min=precio_min, precio_max=precio_max,
        solo_vendidos=solo_vendidos, ordenar_por=ordenar_por,
        proveedores_ids=proveedores_ids, fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin, disponibilidad=disponibilidad,
    )

@producto_routers.get("/stock/{stock_id}")
def obtener_stock_endpoint(stock_id: int, db: Session = Depends(get_session)):
    """Obtener detalle de un stock individual (Usa este antes del ID de producto)."""
    stock_data = obtener_stock_detalle(db, stock_id)
    if not stock_data:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return stock_data

@producto_routers.get("/", response_model=PaginatedProductosResponse)
def listar_productos_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tipo_busqueda: str = Query("producto_id"),
    categoria_id: Optional[int] = Query(None),
    marca_id: Optional[int] = Query(None),
    color: Optional[str] = Query(None),
    talla: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    material: Optional[str] = Query(None),
    precio_min: Optional[float] = Query(None),
    precio_max: Optional[float] = Query(None),
    solo_vendidos: bool = Query(False),
    ordenar_por: str = Query("fecha_desc"),
    proveedores_ids: List[int] = Query(default=[]),
    fecha_inicio: Optional[str] = Query(None),
    fecha_fin: Optional[str] = Query(None),
    disponibilidad: Optional[str] = Query("todos"),
    db: Session = Depends(get_session)
):
    """Vista de catálogo maestro."""
    return obtener_productos_paginados(
        db=db, page=page, limit=limit, search=search,
        tipo_busqueda=tipo_busqueda, categoria_id=categoria_id,
        marca_id=marca_id, color=color, talla=talla, estado=estado,
        material=material, precio_min=precio_min, precio_max=precio_max,
        solo_vendidos=solo_vendidos, ordenar_por=ordenar_por,
        proveedores_ids=proveedores_ids, fecha_inicio=fecha_inicio,
        disponibilidad=disponibilidad, fecha_fin=fecha_fin,
    )

@producto_routers.get("/{producto_id}")
def obtener_producto_endpoint(producto_id: int, db: Session = Depends(get_session)):
    """Obtener producto completo con variantes y stocks."""
    producto = obtener_producto_completo(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# =====================================================
# ✍️ RUTAS DE ESCRITURA (POST / PUT)
# =====================================================

@producto_routers.post("/")
async def crear_producto_endpoint(request: Request, db: Session = Depends(get_session)):
    """Creación de producto con soporte para ropa Nueva, Segunda Mano y Vintage."""
    form = await request.form()
    
    # 1. Manejo dinámico de imágenes (lo que ya tenías)
    archivos_dict = {k: [v] for k, v in form.multi_items() if k.startswith("file_")}

    # 2. Conversión segura de es_vintage (de string a booleano)
    es_vintage_raw = form.get("es_vintage", "false").lower()
    es_vintage = es_vintage_raw in ["true", "on", "1"]

    # 3. Llamada al repositorio con los nuevos campos
    producto = crear_producto(
        db=db,
        nombre=form.get("nombre"),
        descripcion=form.get("descripcion"),
        tipo=form.get("tipo"),
        categoria_id=int(form.get("categoria_id")),
        publico_objetivo=form.get("publico_objetivo"),
        marca_id=form.get("marca_id"),
        marca_nombre=form.get("marca_nombre"),
        variantes=form.get("variantes"),
        imagenes=archivos_dict,
        estado=form.get("estado"), # "nuevo", "usado", "vintage"
        es_vintage=es_vintage,      # ✨ NUEVO
        epoca=form.get("epoca")     # ✨ NUEVO (ej: "90s", "Y2K", None)
    )
    
    return {"mensaje": "Producto creado con éxito", "producto_id": producto.id}



@producto_routers.put("/stock/{stock_id}")
def editar_stock_endpoint(stock_id: int, payload: StockEditPayload, db: Session = Depends(get_session)):
    """Edición rápida de una talla/stock individual."""
    actualizado = actualizar_stock_individual(db, stock_id, payload.model_dump())
    if not actualizado:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return {"mensaje": "Stock actualizado correctamente"}



@producto_routers.put("/{producto_id}")
async def editar_producto_endpoint(
    producto_id: int,
    request: Request,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin),
    publico_objetivo: str = Form(...),
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    categoria_id: Optional[int] = Form(None),
    marca_id: Optional[int] = Form(None),
    marca_nombre: Optional[str] = Form(None),
    tipo: Optional[str] = Form(None),
    variantes: Optional[str] = Form(None),
    estado: str = Form(...),
    es_vintage: bool = Form(False), 
    epoca: Optional[str] = Form(None)
):
    """Edición completa de producto y sus ramas."""
    try:
        form_data = await request.form()
        
        es_vintage_bool = str(form_data.get("es_vintage", "false")).lower() in ["true", "on", "1"]

        # ✨ EL ARREGLO: Cambiamos "imagenes_" por "file_"
        imagenes_dict = {}
        for key, value in form_data.multi_items():
            if key.startswith("file_"):  # <--- CORRECCIÓN AQUÍ
                if key not in imagenes_dict:
                    imagenes_dict[key] = []
                imagenes_dict[key].append(value)

        # ✨ Llamada al repo usando las variables limpias
        producto = editar_producto_completo(
            db=db, 
            producto_id=producto_id, 
            nombre=nombre,
            descripcion=descripcion, 
            estado=estado, 
            categoria_id=categoria_id,
            publico_objetivo=publico_objetivo, 
            marca_id=marca_id,
            marca_nombre=marca_nombre, 
            tipo=tipo, 
            variantes=variantes,
            imagenes=imagenes_dict, # <--- ¡Ahora sí va lleno de archivos!
            es_vintage=es_vintage_bool,
            epoca=epoca                
        )
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {"mensaje": "Producto actualizado correctamente", "producto_id": producto.id}

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error de integridad: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ==========================================
# 🗑️ GESTIÓN DE PAPELERA (SOFT DELETE)
# ==========================================

@producto_routers.put("/{producto_id}/papelera")
def enviar_producto_a_papelera(producto_id: int, db: Session = Depends(get_session)):
    return mover_producto_papelera(db, producto_id)

@producto_routers.put("/variante/{variante_id}/papelera")
def enviar_variante_a_papelera(variante_id: int, db: Session = Depends(get_session)):
    return mover_variante_papelera(db, variante_id)

@producto_routers.put("/stock/{stock_id}/papelera")
def enviar_stock_a_papelera(stock_id: int, db: Session = Depends(get_session)):
    return mover_stock_papelera(db, stock_id)

# ==========================================
# ♻️ RESTAURAR
# ==========================================

@producto_routers.put("/{producto_id}/restaurar")
def restaurar_producto(producto_id: int, db: Session = Depends(get_session)):
    return restaurar_producto_papelera(db, producto_id)

@producto_routers.put("/variante/{variante_id}/restaurar")
def restaurar_variante(variante_id: int, db: Session = Depends(get_session)):
    return restaurar_variante_papelera(db, variante_id)

@producto_routers.put("/stock/{stock_id}/restaurar")
def restaurar_stock(stock_id: int, db: Session = Depends(get_session)):
    return restaurar_stock_papelera(db, stock_id)

# ==========================================
# 💥 ELIMINACIÓN PERMANENTE (HARD DELETE)
# ==========================================

@producto_routers.delete("/papelera/{producto_id}")
def destruir_producto(producto_id: int, db: Session = Depends(get_session)):
    res = destruir_producto_total(db, producto_id)
    if not res.get("success"): 
        raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res

@producto_routers.delete("/papelera/variante/{variante_id}")
def destruir_variante(variante_id: int, db: Session = Depends(get_session)):
    res = destruir_variante_total(db, variante_id)
    if not res.get("success"): 
        raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res

@producto_routers.delete("/papelera/stock/{stock_id}")
def destruir_stock(stock_id: int, db: Session = Depends(get_session)):
    res = destruir_stock_total(db, stock_id)
    if not res.get("success"): 
        raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res