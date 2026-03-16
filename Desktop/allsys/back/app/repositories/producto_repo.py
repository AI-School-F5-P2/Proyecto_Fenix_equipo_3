import json
import random
import string
from typing import Dict, List, Optional
from fastapi import HTTPException # Añadimos esto para lanzar errores
from pydantic import ValidationError # Añadimos esto
from sqlalchemy.orm import Session, joinedload
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.stock_model import Stock
from app.models.atributo_model import Atributo, ValorAtributo
from app.models.marcas_model import Marca
from app.models.variante_imagen_model import Imagen
from app.schemas.variante_schema import VarianteSchema
from app.services.s3_service import delete_image_from_s3, upload_image_to_s3
from app.repositories.proveedores_repo import buscar_o_crear
from app.repositories.marcas_repo import crear_marca

# =====================================================
# SKU GENERATOR
# =====================================================
def generar_sku(tipo: str, id_unico: int) -> str:
    prefijo = tipo[:3].upper() if tipo else "GEN"
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"{prefijo}-{rand}-{id_unico}"

# =====================================================
# HELPERS: VALORES DE ATRIBUTOS (EAV)
# =====================================================
def guardar_valores_stock(db: Session, stock_obj: Stock, atributos_data: list):
    db.query(ValorAtributo).filter_by(stock_id=stock_obj.id).delete()
    for attr in atributos_data:
        if not attr.get("valor"): continue 

        nombre_attr = attr["nombre"].strip().lower()
        atributo_base = db.query(Atributo).filter(Atributo.nombre == nombre_attr).first()
        
        if not atributo_base:
            atributo_base = Atributo(nombre=nombre_attr)
            db.add(atributo_base)
            db.flush()

        nuevo_valor = ValorAtributo(
            stock_id=stock_obj.id,
            atributo_id=atributo_base.id,
            valor=str(attr["valor"]).strip()
        )
        db.add(nuevo_valor)

# =====================================================
# CREAR PRODUCTO COMPLETO
# =====================================================
# app/repositories/producto_repo.py

def crear_producto(
    db: Session, nombre: str, estado: str, descripcion: Optional[str], categoria_id: int, tipo: str, 
    publico_objetivo: str, variantes: str, marca_id: Optional[int] = None, 
    marca_nombre: Optional[str] = None, imagenes: Optional[Dict[str, List]] = None
):
    # 1. Validaciones Generales relativas
    # ✨ LA DESCRIPCIÓN YA NO ES OBLIGATORIA AQUÍ
    desc_final = descripcion.strip() if descripcion else ""
    
    if not publico_objetivo or not publico_objetivo.strip():
        raise HTTPException(status_code=400, detail="El público objetivo es obligatorio.")

    # 2. Validar JSON de variantes
    try:
        variantes_json = json.loads(variantes)
        variantes_validadas = [VarianteSchema(**v) for v in variantes_json] 
    except ValidationError as e:
        error_msg = e.errors()[0].get("msg", "Datos de variante inválidos")
        raise HTTPException(status_code=400, detail=f"Error en variantes: {error_msg}")

    # 3. Lógica de Marca
    if not marca_id and marca_nombre:
        nombre_clean = marca_nombre.strip()
        marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
        marca_id = marca_existente.id if marca_existente else crear_marca(db, nombre=nombre_clean).id

    # 4. Crear Producto
    producto = Producto(
        nombre=nombre.strip(), 
        descripcion=desc_final, 
        categoria_id=categoria_id,
        marca_id=marca_id, 
        estado=estado,         # ✨ ASEGÚRATE QUE EN TU MODELO SEA 'estado'
        tipo=tipo, 
        publico_objetivo=publico_objetivo,
        sku="TEMP"
    )
    db.add(producto)
    db.flush()
    producto.sku = generar_sku(tipo, producto.id)

    # 5. Bucle de Variantes
    for v_data in variantes_validadas:
        # ✨ REGLA: Descripción de variante OBLIGATORIA
        if not v_data.descripcion or not v_data.descripcion.strip():
            raise HTTPException(status_code=400, detail="Cada variante debe tener su propia descripción.")

        nueva_variante = Variante(
            producto_id=producto.id,
            sku="TEMP",
            hex_identidad=v_data.hex_identidad,           
            identidad_variante=v_data.identidad_variante, 
            ubicacion=v_data.ubicacion,
            descripcion=v_data.descripcion.strip() # ✨ Guardamos la desc de la variante
        )
        db.add(nueva_variante)
        db.flush()
        nueva_variante.sku = generar_sku(tipo, nueva_variante.id)

        for s_data in v_data.stocks:
            # ✨ REGLA: Stock debe ser > 0
            if s_data.stock <= 0:
                raise HTTPException(status_code=400, detail="El stock debe ser mayor a 0.")

            p_id = s_data.proveedor_id
            if not p_id:
                nombre_p = s_data.proveedor_nombre_nuevo or s_data.proveedor
                proveedor_obj = buscar_o_crear(db, nombre_p)
                p_id = proveedor_obj.id if proveedor_obj else None

            stock_obj = Stock(
                variante_id=nueva_variante.id,
                proveedor_id=p_id,
                etiqueta=s_data.etiqueta,
                cantidad=s_data.stock, # Mapeamos 'stock' del JSON a 'cantidad' en DB
                precio_compra=s_data.precio_compra,
                precio_venta=s_data.precio_venta,
                fecha_compra=s_data.fecha_compra,
                publicar_web=s_data.publicar_web,
                publicar_vinted=s_data.publicar_vinted,
                publicar_wallapop=s_data.publicar_wallapop,
                sku="TEMP"
            )
            db.add(stock_obj)
            db.flush()
            stock_obj.sku = generar_sku(tipo, stock_obj.id)

            if s_data.atributos:
                attr_dicts = [{"nombre": a.nombre, "valor": a.valor} for a in s_data.atributos]
                guardar_valores_stock(db, stock_obj, attr_dicts)

        # Imágenes
        if imagenes and v_data.temp_id in imagenes:
            for file in imagenes[v_data.temp_id]:
                url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{nueva_variante.id}")
                db.add(Imagen(url=url, variante_id=nueva_variante.id))

    db.commit()
    db.refresh(producto)
    return producto

# =====================================================
# LISTADO PAGINADO
# =====================================================
def obtener_productos_paginados(db: Session, page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    query = (
        db.query(Producto)
        .filter(Producto.activo == True)
        .options(
            joinedload(Producto.categoria),
            joinedload(Producto.marca),
            joinedload(Producto.variantes).joinedload(Variante.stocks).joinedload(Stock.valores),
            joinedload(Producto.variantes).joinedload(Variante.imagenes)
        )
        .order_by(Producto.id.desc())
    )

    total = query.count()
    productos = query.offset(offset).limit(limit).all()

    resultados = []
    for p in productos:
        stock_acumulado = sum(s.cantidad for v in p.variantes for s in v.stocks)
        precios = [s.precio_venta for v in p.variantes for s in v.stocks]
        imagen_cover = p.variantes[0].imagenes[0].url if (p.variantes and p.variantes[0].imagenes) else None
        colores_unicos = list({v.hex_identidad for v in p.variantes if v.hex_identidad})
        # Verificamos canales de publicación (si al menos un stock lo tiene en True)
        publicado_web = any(s.publicar_web for v in p.variantes for s in v.stocks)
        publicado_vinted = any(s.publicar_vinted for v in p.variantes for s in v.stocks)
        publicado_wallapop = any(s.publicar_wallapop for v in p.variantes for s in v.stocks)

        resultados.append({
            "id": p.id,
            "nombre": p.nombre,
            "sku": p.sku,
            "tipo": p.tipo,
            "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
            "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
            "imagen": imagen_cover,
            "stock_total": stock_acumulado,
            "precio_min": min(precios) if precios else None,
            "precio_max": max(precios) if precios else None,
            "colores": colores_unicos,
            "canales": {
                "web": publicado_web,
                "vinted": publicado_vinted,
                "wallapop": publicado_wallapop
            }
        })

    return {"total": total, "items": resultados}

# =====================================================
# DETALLE COMPLETO (Para Edición)
# =====================================================
def obtener_producto_completo(db: Session, p_id: int):
    producto = (
        db.query(Producto)
        .options(
            joinedload(Producto.categoria),
            joinedload(Producto.marca),
            joinedload(Producto.variantes)
                .joinedload(Variante.stocks)
                .joinedload(Stock.valores)
                .joinedload(ValorAtributo.atributo),
            joinedload(Producto.variantes).joinedload(Variante.imagenes)
        )
        .filter(Producto.id == p_id)
        .first()
    )

    if not producto: return None

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "descripcion": producto.descripcion,
        "tipo": producto.tipo,
        "estado": producto.estado,
        "publico_objetivo": producto.publico_objetivo, # ✨ Enviado al front
        "categoria_id": producto.categoria_id,
        "marca":producto.marca,
        "variantes": [
            {
                "id": v.id,
                "hex_identidad": v.hex_identidad,           # ✨ Actualizado
                "identidad_variante": v.identidad_variante, # ✨ Actualizado
                "ubicacion": v.ubicacion,
                "descripcion":v.descripcion,
                "imagenes": [img.url for img in v.imagenes],
                "stocks": [
                    {
                        
                        "id": s.id,
                        "sku": s.sku,
                        "etiqueta": s.etiqueta,
                        "cantidad": s.cantidad,
                        "precio_compra": s.precio_compra,
                        "precio_venta": s.precio_venta,
                        "descuento":s.descuento,
                        "proveedor_id": s.proveedor_id,
                        "publicar_web": s.publicar_web,
                        "publicar_vinted": s.publicar_vinted,
                        "publicar_wallapop": s.publicar_wallapop,
                        # ✨ Aseguramos que se envía al front en formato string para que el input type="date" lo lea
                        "fecha_compra": s.fecha_compra.isoformat() if s.fecha_compra else None,
                        "atributos": [{"nombre": val.atributo.nombre, "valor": val.valor} for val in s.valores]
                    } for s in v.stocks if s.activo
                ]
            } for v in producto.variantes if v.activo
        ]
    }

# =====================================================
# EDITAR PRODUCTO COMPLETO
# =====================================================
import json
import random
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

def editar_producto_completo(
    db: Session, 
    producto_id: int, 
    nombre: str, 
    descripcion: str, 
    categoria_id: int, 
    tipo: str, 
    estado: str,
    publico_objetivo: str, 
    variantes: str, 
    marca_id: Optional[int] = None, 
    marca_nombre: Optional[str] = None, 
    imagenes: Optional[Dict[str, List]] = None
):
    # 1. Buscar el producto existente
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return None

    # 2. Actualizar campos básicos del producto
    producto.nombre = nombre
    producto.descripcion = descripcion
    producto.categoria_id = categoria_id
    producto.tipo = tipo
    producto.estado = estado
    producto.publico_objetivo = publico_objetivo
    
    # 3. Lógica de Marca (Corregida: Evita asignar ID 0 si falla el frontend)
    if marca_id and marca_id > 0:
        producto.marca_id = marca_id
    elif marca_nombre and marca_nombre.strip():
        nombre_clean = marca_nombre.strip()
        marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
        if marca_existente:
            producto.marca_id = marca_existente.id
        else:
            nueva_m = crear_marca(db, nombre=nombre_clean)
            producto.marca_id = nueva_m.id

    # 4. Procesar Variantes (JSON)
    variantes_data = json.loads(variantes)
    ids_variantes_vienen = [v.get("id") for v in variantes_data if v.get("id")]
    
    # Eliminar variantes que ya no están en la lista enviada
    for v_old in producto.variantes:
        if v_old.id not in ids_variantes_vienen:
            v_old.activo = False  # Lo apagamos

    for v_data in variantes_data:
        v_id = v_data.get("id")
        v_temp_id = str(v_data.get("temp_id"))
        
        # Crear o Actualizar Variante
        if v_id:
            nv = db.query(Variante).filter(Variante.id == v_id).first()
            if nv:
                nv.hex_identidad = v_data.get("hex_identidad")
                nv.identidad_variante = v_data.get("identidad_variante")
                nv.ubicacion = v_data.get("ubicacion")
                nv.descripcion = v_data.get("descripcion")
        else:
            nv = Variante(
                producto_id=producto.id,
                sku=generar_sku(tipo, random.randint(100, 999)), # SKU Temporal
                hex_identidad=v_data.get("hex_identidad"),
                identidad_variante=v_data.get("identidad_variante"),
                ubicacion=v_data.get("ubicacion"),
                descripcion=v_data.get("descripcion")
            )
            db.add(nv)
            db.flush() # Para obtener el ID de la nueva variante
            nv.sku = generar_sku(tipo, nv.id)

        # Obtenemos las URLs que Angular nos manda (las que el usuario NO borró)
        urls_que_se_quedan = v_data.get("imagenes", [])
        
        # Buscamos todas las imágenes actuales de esta variante en la DB
        imagenes_en_db = db.query(Imagen).filter(Imagen.variante_id == nv.id).all()
        
        for img_db in imagenes_en_db:
            if img_db.url not in urls_que_se_quedan:
                # ¡El usuario la borró en el Frontend!
                
                # A) Primero la borramos de Amazon S3 (Envuelto en try/except por seguridad)
                try:
                    delete_image_from_s3(img_db.url)
                    print(f"🗑️ ÉXITO: Imagen borrada de S3 -> {img_db.url}")
                except Exception as e:
                    print(f"⚠️ ADVERTENCIA: No se pudo borrar de S3 (Quizás ya no existía) -> {e}")
                
                # B) Luego la borramos de nuestra tabla en MySQL/Postgres
                db.delete(img_db)

        # 5. Procesar Stocks dentro de la variante
        stocks_data = v_data.get("stocks", [])
        ids_stocks_vienen = [s.get("id") for s in stocks_data if s.get("id")]
        
        # Eliminar registros de stock que no vienen en el JSON
        db.query(Stock).filter(
            Stock.variante_id == nv.id, 
            Stock.id.notin_(ids_stocks_vienen) if ids_stocks_vienen else Stock.id > 0
        ).update({"activo": False}, synchronize_session=False)

        for s_data in stocks_data:
            s_id = s_data.get("id")
            
            # Gestión de Proveedor
            p_id = s_data.get("proveedor_id")
            if not p_id or p_id == 0:
                nombre_p = s_data.get("proveedor_nombre_nuevo") or s_data.get("proveedor")
                if nombre_p:
                    proveedor_obj = buscar_o_crear(db, nombre_p)
                    p_id = proveedor_obj.id if proveedor_obj else None

            fecha_c = s_data.get("fecha_compra")
            if not fecha_c: fecha_c = None

            if s_id:
                # Actualizar Stock existente
                so = db.query(Stock).filter(Stock.id == s_id).first()
                if so:
                    so.etiqueta = s_data.get("etiqueta")
                    # ✨ CAMBIO CLAVE: Usamos 'cantidad' porque es lo que envía Angular
                    so.cantidad = s_data.get("cantidad", 0) 
                    so.precio_compra = s_data.get("precio_compra", 0)
                    so.precio_venta = s_data.get("precio_venta", 0)
                    so.proveedor_id = p_id
                    so.fecha_compra = fecha_c
                    so.descuento = s_data.get("descuento", 0)
            else:
                # Crear nuevo registro de Stock
                so = Stock(
                    variante_id=nv.id, 
                    proveedor_id=p_id,
                    etiqueta=s_data.get("etiqueta", "Única"),
                    # ✨ CAMBIO CLAVE: Usamos 'cantidad'
                    cantidad=s_data.get("cantidad", 0),
                    precio_compra=s_data.get("precio_compra", 0),
                    precio_venta=s_data.get("precio_venta", 0),
                    fecha_compra=fecha_c,
                    sku=generar_sku(tipo, random.randint(100, 999))
                )
                db.add(so)
                db.flush()
                so.sku = generar_sku(tipo, so.id)

            # Actualizar Atributos (Talla, Material, etc.)
            if s_data.get("atributos"):
                guardar_valores_stock(db, so, s_data.get("atributos"))

        # 6. Procesar nuevas imágenes si existen
        if imagenes and v_temp_id in imagenes:
            for file in imagenes[v_temp_id]:
                url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{nv.id}")
                db.add(Imagen(url=url, variante_id=nv.id))

    # 7. Confirmar cambios en la DB
    db.commit()
    db.refresh(producto)
    return producto

# =====================================================
# ELIMINAR PRODUCTO
# =====================================================
# =====================================================
# ELIMINAR PRODUCTO (BORRADO LÓGICO + LIMPIEZA S3)
# =====================================================
def eliminar_producto(db: Session, p_id: int):
    # 1. Buscamos el producto con todas sus relaciones
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: 
        return False
    
    # 2. MARCAR COMO INACTIVO (Borrado Lógico)
    producto.activo = False
    
    # 3. LIMPIEZA INTELIGENTE DE ALMACENAMIENTO (S3)
    # Recorremos cada variante para reducir su galería de fotos
    for variante in producto.variantes:
        # También marcamos la variante y sus stocks como inactivos por seguridad
        variante.activo = False
        for s in variante.stocks:
            s.activo = False

        # Lógica de imágenes:
        # Si la variante tiene más de una imagen, borramos las sobrantes de S3 y DB
        if len(variante.imagenes) > 1:
            # Mantenemos la primera (variante.imagenes[0]) y procesamos las demás
            imagenes_sobrantes = variante.imagenes[1:] 
            
            for img in imagenes_sobrantes:
                # A) Borramos el archivo físico en Amazon S3
                try:
                    delete_image_from_s3(img.url)
                    print(f"🧹 S3: Borrada imagen sobrante -> {img.url}")
                except Exception as e:
                    print(f"⚠️ Error al borrar de S3: {e}")
                
                # B) Borramos el registro de la tabla de imágenes
                db.delete(img)

    # 4. Guardamos los cambios
    db.commit()
    return True