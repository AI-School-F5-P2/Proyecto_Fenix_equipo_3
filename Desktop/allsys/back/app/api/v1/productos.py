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
    editar_producto_completo,
    obtener_producto_completo,
    obtener_productos_paginados,
    eliminar_producto
)
from app.schemas.producto_schema import PaginatedProductosResponse

producto_routers = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# =====================================================
# CREAR PRODUCTO
# =====================================================
@producto_routers.post("/")
async def crear_producto_endpoint(request: Request, db: Session = Depends(get_session),):
    # ---------------------------
    # Recibimos todo dinámicamente
    # ---------------------------
    form = await request.form()
    
    # Campos básicos
    nombre = form.get("nombre")
    descripcion = form.get("descripcion")
    tipo = form.get("tipo")
    categoria_id = form.get("categoria_id")
    publico_objetivo = form.get("publico_objetivo")
    # Marca: puede venir como id o como nombre
    marca_id = form.get("marca_id")
    marca_nombre = form.get("marca_nombre")
    estado = form.get("estado")
    variantes_json = form.get("variantes")


    # Si por algún motivo llegara vacío, le damos un valor por defecto
    if not estado:
        estado = "nuevo"
    
    # ---------------------------
    # Extraer archivos por temp_id
    # ---------------------------
    archivos_por_variante = {}
    for key, value in form.multi_items():
        if key.startswith("imagenes_"):
            temp_id = key.replace("imagenes_", "")
            archivos_por_variante.setdefault(temp_id, []).append(value)
    
    # ---------------------------
    # Debug: imprimir datos crudos
    # ---------------------------
    print("===== DATOS DEL FORMULARIO CRUDO =====")
    print("Nombre:", nombre)
    print("Descripcion:", descripcion)
    print("Tipo:", tipo)
    print("Categoria ID:", categoria_id)
    print("Marca ID:", marca_id)
    print("genero:", publico_objetivo)
    print("Marca Nombre:", marca_nombre)
    print("Variantes (JSON crudo):", variantes_json)
    print("Archivos por variante:")
    for temp_id, files in archivos_por_variante.items():
        print(f"- Variante {temp_id}: {[file.filename for file in files]}")
    print("======================================\n")
    
    # ---------------------------
    # Parseamos el JSON de variantes
    # ---------------------------
    try:
        variantes_data = json.loads(variantes_json)
        # Asociamos los archivos a cada variante según temp_id
        for variante in variantes_data:
            temp_id = variante.get("temp_id")
            variante["imagenes_files"] = archivos_por_variante.get(temp_id, [])
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear variantes JSON: {e}")


    # ---------------------------
    # Aquí podrías llamar a tu función para crear el producto
    producto = crear_producto(
                              db=db,
                              nombre=nombre, 
                              descripcion=descripcion, 
                              tipo=tipo, 
                              categoria_id=categoria_id, 
                              marca_id=marca_id, 
                              marca_nombre=marca_nombre,
                              variantes=variantes_json,
                              imagenes=archivos_por_variante,
                              publico_objetivo=publico_objetivo,
                              estado=estado
                              )
    # ---------------------------


    return {
        "mensaje": "Producto creado correctamente",
        "producto_id": producto
    }

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
# LISTAR PRODUCTOS (PAGINADO)
# =====================================================
@producto_routers.get("/", response_model=PaginatedProductosResponse)
def listar_productos_endpoint(
    # Exigimos que la página sea mínimo 1
    page: int = Query(1, ge=1, description="Número de página"),
    # Exigimos que el límite sea mínimo 1 y máximo 100 por seguridad
    limit: int = Query(10, ge=1, le=100, description="Cantidad de ítems por página"),
    db: Session = Depends(get_session)
):
    return obtener_productos_paginados(db, page, limit)


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

# =====================================================
# ELIMINAR PRODUCTO
# =====================================================
@producto_routers.delete("/{producto_id}")
def eliminar_producto_endpoint(
    producto_id: int,
    db: Session = Depends(get_session),
    current_admin=Depends(get_current_admin)
):
    eliminado = eliminar_producto(db, producto_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    return {
        "mensaje": "Producto eliminado correctamente"
    }
