import json
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile,
    HTTPException,
    Query,
    Request
)
from sqlalchemy.orm import Session

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
    vaciar_producto_papelera
)

from app.schemas.producto_schema import (
    PaginatedProductosResponse, 
    PaginatedStockResponse,
    StockEditPayload  # ✨ AGREGAMOS ESTA LÍNEA
)

producto_routers = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)





















@producto_routers.get("/papelera")
def listar_papelera_endpoint(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin)
):
    """
    Devuelve los productos que han sido movidos a la papelera (Soft Delete).
    """
    return obtener_productos_papelera(db, page=page, limit=limit)



# =====================================================
# LISTAR STOCKS VENDIBLES (VISTA APLANADA / INVENTARIO)
# =====================================================
@producto_routers.get("/inventario-individual", response_model=PaginatedStockResponse)
def listar_inventario_individual_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    tipo_busqueda: str = Query("stock_id"), # Valor por defecto acorde a la vista
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
    fecha_inicio: Optional[str] = Query(None), # ✨ NUEVO
    fecha_fin: Optional[str] = Query(None),
    disponibilidad: Optional[str] = Query("todos"),
    db: Session = Depends(get_session)
):
    return obtener_stocks_individuales_paginados(
        db=db, 
        page=page, 
        limit=limit, 
        search=search, 
        tipo_busqueda=tipo_busqueda,
        categoria_id=categoria_id,
        marca_id=marca_id,
        color=color,
        talla=talla,
        estado=estado,
        precio_min=precio_min,
        precio_max=precio_max,
        solo_vendidos=solo_vendidos,
        ordenar_por=ordenar_por,
        proveedores_ids=proveedores_ids,
        fecha_inicio = fecha_inicio, # ✨ NUEVO
        fecha_fin = fecha_fin,
        disponibilidad=disponibilidad,
    )

# =====================================================
# LISTAR PRODUCTOS (VISTA MAESTRA / CATÁLOGO)
# =====================================================
@producto_routers.get("/", response_model=PaginatedProductosResponse)
def listar_productos_endpoint(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tipo_busqueda: str = Query("producto_id"), # Valor por defecto acorde a la vista
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
    fecha_inicio: Optional[str] = Query(None), # ✨ NUEVO
    fecha_fin: Optional[str] = Query(None),
    disponibilidad: Optional[str] = Query("todos"),
    db: Session = Depends(get_session)
):
    return obtener_productos_paginados(
        db=db, 
        page=page, 
        limit=limit, 
        search=search,
        tipo_busqueda=tipo_busqueda,
        categoria_id=categoria_id,
        marca_id=marca_id,
        color=color,
        talla=talla,
        estado=estado,
        material=material,
        precio_min=precio_min,
        precio_max=precio_max,
        solo_vendidos=solo_vendidos,
        ordenar_por=ordenar_por,
        proveedores_ids=proveedores_ids,
        fecha_inicio = fecha_inicio, # ✨ NUEVO
        disponibilidad=disponibilidad,
        fecha_fin = fecha_fin,
    )
























# =====================================================
# CREAR PRODUCTO
# =====================================================
# app/api/v1/productos.py

# --- REEMPLAZA EL CONTENIDO DE crear_producto_endpoint ---
@producto_routers.post("/")
async def crear_producto_endpoint(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    
    # 1. Atrapamos TODOS los archivos que empiecen con "file_"
    archivos_dict = {}
    for key, value in form.multi_items():
        if key.startswith("file_"):
            # Guardamos la clave completa: "file_UUID_NUEVA_0"
            archivos_dict[key] = [value] 

    # 2. Llamamos al repo (pasamos los campos uno a uno)
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
        imagenes=archivos_dict, # Enviamos el dict con las claves "file_..."
        estado=form.get("estado")
    )

    return {"mensaje": "Producto creado", "producto_id": producto.id}

# --- REEMPLAZA EL CONTENIDO DE editar_producto_endpoint ---
@producto_routers.put("/{producto_id}")
async def editar_producto_endpoint(producto_id: int, request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    
    archivos_dict = {}
    for key, value in form.multi_items():
        if key.startswith("file_"):
            archivos_dict[key] = [value]

    producto = editar_producto_completo(
        db=db,
        producto_id=producto_id,
        nombre=form.get("nombre"),
        descripcion=form.get("descripcion"),
        categoria_id=int(form.get("categoria_id")),
        tipo=form.get("tipo"),
        estado=form.get("estado"),
        publico_objetivo=form.get("publico_objetivo"),
        variantes=form.get("variantes"),
        marca_id=form.get("marca_id"),
        marca_nombre=form.get("marca_nombre"),
        imagenes=archivos_dict
    )
    return {"mensaje": "Actualizado", "producto_id": producto.id}






# =====================================================
# OBTENER DETALLE DE UN STOCK ESPECÍFICO (¡Va antes del /{producto_id}!)
# =====================================================
@producto_routers.get("/stock/{stock_id}")
def obtener_stock_endpoint(
    stock_id: int,
    db: Session = Depends(get_session)
):
    stock_data = obtener_stock_detalle(db, stock_id)
    if not stock_data:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return stock_data


from pydantic import BaseModel

class StockEditPayload(BaseModel):
    cantidad: int
    precio_compra: float
    precio_venta: float
    descuento: float = 0
    ubicacion: Optional[str] = ""
    proveedor_id: Optional[int] = None
    proveedor_nombre_nuevo: Optional[str] = None
    publicar_web: bool = False
    publicar_vinted: bool = False
    publicar_wallapop: bool = False

@producto_routers.put("/stock/{stock_id}")
def editar_stock_endpoint(
    stock_id: int, 
    payload: StockEditPayload, 
    db: Session = Depends(get_session)
):
    from app.repositories.producto_repo import actualizar_stock_individual
    actualizado = actualizar_stock_individual(db, stock_id, payload.dict())
    if not actualizado:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    return {"mensaje": "Stock actualizado"}




# =====================================================
# EDITAR STOCK INDIVIDUAL (Inventario Rápido)
# =====================================================
@producto_routers.put("/stock/{stock_id}")
def editar_stock_endpoint(
    stock_id: int, 
    payload: StockEditPayload, # ✨ Usa el esquema importado
    db: Session = Depends(get_session)
):
    from app.repositories.producto_repo import actualizar_stock_individual
    
    # Pasamos los datos validados como diccionario al repo
    actualizado = actualizar_stock_individual(db, stock_id, payload.model_dump()) 
    # NOTA: Usa .dict() si estás en Pydantic v1, o .model_dump() si estás en Pydantic v2
    
    if not actualizado:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
        
    return {"mensaje": "Stock actualizado correctamente"}






# =====================================================
# OBTENER PRODUCTO COMPLETO
# =====================================================
@producto_routers.get("/{producto_id}")
def obtener_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_session)
):
    
    producto = obtener_producto_completo(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto



# =====================================================
# EDITAR PRODUCTO COMPLETO
# =====================================================
from sqlalchemy.exc import IntegrityError  # 👈 Importante: Agrega esta importación arriba
import traceback # Para ver el rastro del error si es necesario
from fastapi import Request # ✨ 1. Asegúrate de importar Request arriba del todo

@producto_routers.put("/{producto_id}")
async def editar_producto_endpoint( # ✨ 2. DEBE SER 'async def' para poder leer el request
    producto_id: int,
    request: Request, # ✨ 3. Añadimos esto para leer el formulario crudo
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
    estado: str = Form(...)
    # ❌ 4. BORRAMOS LA LÍNEA DE 'imagenes: Optional[...]'
):
    try:
        # ✨ 5. ATRAPAMOS LAS FOTOS DINÁMICAS AQUÍ
        form_data = await request.form()

        # 🧪 PRINT DE SEGURIDAD 2: Ver lo que llega al endpoint
        print("\n=== 📥 RECIBIDO EN ENDPOINT ===")
        print(f"Variantes JSON: {form_data.get('variantes')}")
        
        imagenes_dict = {}
        
        for key, value in form_data.multi_items():
            # Buscamos todo lo que empiece por "imagenes_"
            if key.startswith("imagenes_"):
                temp_id = key.replace("imagenes_", "") # Sacamos el código de la variante
                if temp_id not in imagenes_dict:
                    imagenes_dict[temp_id] = []
                imagenes_dict[temp_id].append(value)
                
        print(f"DEBUG: marca_id recibido -> {marca_id} (Tipo: {type(marca_id)})")
        print(f"DEBUG: Diccionario de imágenes armadas -> {imagenes_dict}") # Para que lo veas en consola
        
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
            imagenes=imagenes_dict # ✨ 6. Le pasamos el diccionario armado
        )
        
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        return {
            "mensaje": "Producto actualizado correctamente",
            "producto_id": producto.id
        }

    except IntegrityError as e:
        db.rollback() 
        print("\n" + "="*60)
        print("❌ ERROR DE INTEGRIDAD (FOREIGN KEY):")
        print(f"MENSAJE ORIGINAL: {e.orig}") 
        print("="*60 + "\n")
        raise HTTPException(
            status_code=400, 
            detail=f"Error de base de datos: {str(e.orig)}"
        )

    except Exception as e:
        db.rollback()
        import traceback # Asegúrate de importar traceback si no lo tienes
        print(f"❌ ERROR GENERAL: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    








# ==========================================
# RUTA: CONSULTAR PAPELERA
# ==========================================



# No olvides importar las nuevas funciones del repo arriba:
# from app.repositories.producto_repo import mover_variante_papelera, mover_stock_papelera, restaurar_producto_papelera, restaurar_variante_papelera, restaurar_stock_papelera, destruir_producto_total, destruir_variante_total, destruir_stock_total

# ==========================================
# 🗑️ MOVER A PAPELERA (SOFT DELETE)
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
# ♻️ RESTAURAR DE PAPELERA
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
# 💥 DESTRUCCIÓN TOTAL (HARD DELETE)
# ==========================================
@producto_routers.delete("/papelera/{producto_id}")
def destruir_producto(producto_id: int, db: Session = Depends(get_session)):
    res = destruir_producto_total(db, producto_id)
    if not res.get("success"): raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res

@producto_routers.delete("/papelera/variante/{variante_id}")
def destruir_variante(variante_id: int, db: Session = Depends(get_session)):
    res = destruir_variante_total(db, variante_id)
    if not res.get("success"): raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res

@producto_routers.delete("/papelera/stock/{stock_id}")
def destruir_stock(stock_id: int, db: Session = Depends(get_session)):
    res = destruir_stock_total(db, stock_id)
    if not res.get("success"): raise HTTPException(status_code=400, detail=res.get("mensaje"))
    return res















