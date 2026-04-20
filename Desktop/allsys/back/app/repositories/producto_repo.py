



import json
import random
import string
from typing import Dict, List, Optional
from fastapi import HTTPException # Añadimos esto para lanzar errores
from pydantic import ValidationError # Añadimos esto
from sqlalchemy.orm import Session, joinedload
from app.models.variantes_model import Variante
from app.models.stock_model import Stock
from app.models.atributo_model import Atributo, ValorAtributo
from app.models.marcas_model import Marca
from app.models.variante_imagen_model import Imagen
from app.schemas.variante_schema import VarianteSchema
from app.services.s3_service import delete_image_from_s3, upload_image_to_s3
from app.repositories.proveedores_repo import buscar_o_crear
from app.repositories.marcas_repo import crear_marca
from app.models.producto_model import Producto
from app.models.ventas_model import DetalleVenta 

# =====================================================
# HELPER: ORDENADOR INTELIGENTE DE TALLAS (NUEVO ✨)
# =====================================================
def ordenar_tallas_logicamente(tallas):
    # Diccionario con el orden oficial de la industria textil
    orden_letras = {
        'xxs': 1, 'xs': 2, 's': 3, 'm': 4, 'l': 5, 'xl': 6, 'xxl': 7, 
        'xxxl': 8, '3xl': 8, '4xl': 9, 'tu': 99, 'unica': 99, 'única': 99
    }

    def obtener_peso(t):
        t_clean = str(t).strip().lower()
        
        # 1. Si es ropa (S, M, L...), usa el diccionario
        if t_clean in orden_letras:
            return (0, orden_letras[t_clean], t)
            
        # 2. Si es calzado o número (38, 40.5...), lo ordena numéricamente
        try:
            return (1, float(t_clean), t)
        except ValueError:
            # 3. Si es texto desconocido, lo manda al final por orden alfabético
            return (2, 0, t)

    # Convertimos el set a lista y lo ordenamos usando las reglas de arriba
    return sorted(list(tallas), key=obtener_peso)

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
# app/repositories/producto_repo.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
# Asegúrate de importar ValorAtributo, Atributo y Stock arriba

def guardar_valores_stock(db: Session, stock_obj: Stock, atributos_data: list):
    """
    Guarda los atributos usando las relaciones Nativas de SQLAlchemy.
    Esto evita los bloqueos de caché ('session state') que hacían que el .delete() fallara.
    """
    try:
        # 1. 🔥 BORRADO NATIVO Y SEGURO: 
        # Vaciamos la lista directamente. Gracias al cascade="delete-orphan" 
        # en el modelo Stock, SQLAlchemy borrará los atributos viejos automáticamente.
        stock_obj.valores = []
        db.flush()

        # 2. 📝 INSERCIÓN DE VALORES NUEVOS
        for attr in atributos_data:
            valor_raw = attr.get("valor")
            if valor_raw is None or str(valor_raw).strip() == "": 
                continue 

            nombre_attr = attr["nombre"].strip().lower()
            
            atributo_base = db.query(Atributo).filter(Atributo.nombre == nombre_attr).first()
            if not atributo_base:
                atributo_base = Atributo(nombre=nombre_attr)
                db.add(atributo_base)
                db.flush() 

            # 3. ✨ AÑADIMOS A LA RELACIÓN (SQLAlchemy se encarga del stock_id)
            nuevo_valor = ValorAtributo(
                atributo_id=atributo_base.id,
                valor=str(valor_raw).strip().upper() 
            )
            stock_obj.valores.append(nuevo_valor)
        
        db.flush()

    except Exception as e:
        db.rollback()
        print(f"❌ Error crítico en atributos EAV: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar atributos: {e}")




















# =====================================================
# CREAR PRODUCTO COMPLETO (CORREGIDA)
# =====================================================
def crear_producto(
    db: Session, 
    nombre: str, 
    estado: str, 
    descripcion: Optional[str], 
    categoria_id: int, 
    tipo: str, 
    publico_objetivo: str, 
    variantes: str, 
    marca_id: Optional[int] = None, 
    marca_nombre: Optional[str] = None, 
    imagenes: Optional[Dict[str, List]] = None, 
    es_vintage: bool = False, 
    epoca: Optional[str] = None
):
    desc_final = descripcion.strip() if descripcion else ""
    
    if not publico_objetivo or not publico_objetivo.strip():
        raise HTTPException(status_code=400, detail="El público objetivo es obligatorio.")

    # 1. VALIDACIÓN Y PARSEO DE VARIANTES
    try:
        variantes_json = json.loads(variantes)
        variantes_validadas = [VarianteSchema(**v) for v in variantes_json] 
    except ValidationError as e:
        # ✨ EL CHIVATO: Extraemos exactamente qué campo falló en el esquema
        campo_fallido = e.errors()[0].get("loc", ["desconocido"])[-1]
        error_msg = e.errors()[0].get("msg", "Datos de variante inválidos")
        raise HTTPException(
            status_code=400, 
            detail=f"Error en la variante (Campo '{campo_fallido}'): {error_msg}"
        )

    # 2. GESTIÓN DE MARCA
    if not marca_id and marca_nombre:
        nombre_clean = marca_nombre.strip()
        marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
        marca_id = marca_existente.id if marca_existente else crear_marca(db, nombre=nombre_clean).id

    # 3. CREACIÓN DEL PRODUCTO PADRE
    producto = Producto(
        nombre=nombre.strip(), 
        descripcion=desc_final, 
        categoria_id=categoria_id,
        marca_id=marca_id, 
        estado=estado,
        es_vintage=es_vintage,
        epoca=epoca,
        tipo=tipo, 
        publico_objetivo=publico_objetivo,
        sku="TEMP"
    )
    db.add(producto)
    db.flush()
    producto.sku = generar_sku(tipo, producto.id)

    # 4. PROCESAMIENTO DE VARIANTES
    for v_data in variantes_validadas:
        if not v_data.descripcion or not v_data.descripcion.strip():
            raise HTTPException(status_code=400, detail="Cada variante debe tener su propia descripción.")

        nueva_variante = Variante(
            producto_id=producto.id,
            sku="TEMP",
            hex_identidad=v_data.hex_identidad,          
            identidad_variante=v_data.identidad_variante, 
            descripcion=v_data.descripcion.strip()
        )
        db.add(nueva_variante)
        db.flush()
        nueva_variante.sku = generar_sku(tipo, nueva_variante.id)

        # 5. PROCESAMIENTO DE STOCKS (Tallas/Medidas)
        for s_data in v_data.stocks:
            # Validación básica de stock físico
            if s_data.stock <= 0:
                raise HTTPException(status_code=400, detail="El stock inicial debe ser mayor a 0.")

            # --- ✨ LÓGICA DE PROVEEDOR Y DUEÑO (CONSIGNACIÓN) ---
            p_id = s_data.proveedor_id
            propietario_id = getattr(s_data, 'propietario_id', None)

            if propietario_id:
                # Si hay un dueño (Merlina), el proveedor no es obligatorio
                # Ignoramos cualquier intento de buscar proveedor mayorista
                p_id = None 
            else:
                # Si es inventario Allsys, buscamos o creamos el proveedor
                if not p_id:
                    nombre_p = s_data.proveedor_nombre_nuevo or s_data.proveedor
                    if nombre_p and nombre_p.strip():
                        proveedor_obj = buscar_o_crear(db, nombre_p.strip(), contexto="inventario")
                        p_id = proveedor_obj.id if proveedor_obj else None

            # Gestión de ID manual (Para migraciones de Excel)
            id_forzado = s_data.id_manual if hasattr(s_data, 'id_manual') and s_data.id_manual else None
            if id_forzado:
                stock_existente = db.query(Stock).filter(Stock.id == id_forzado).first()
                if stock_existente:
                    raise HTTPException(status_code=400, detail=f"El ID manual {id_forzado} ya está en uso.")

            # Crear objeto Stock
            stock_obj = Stock(
                id=id_forzado,
                variante_id=nueva_variante.id,
                proveedor_id=p_id,
                propietario_id=propietario_id, # ✨ ASIGNACIÓN DEL DUEÑO
                ubicacion=s_data.ubicacion,
                etiqueta=s_data.etiqueta,
                cantidad=s_data.stock,
                precio_compra=s_data.precio_compra, # Puede ser 0 si hay propietario_id
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

            # 6. ATRIBUTOS EAV (Talla, Material, etc.)
            if s_data.atributos: # Nota: asegurate si en tu schema es 'atributos' o 'attributes'
                attr_dicts = [{"nombre": a.nombre, "valor": a.valor} for a in s_data.atributos]
                guardar_valores_stock(db, stock_obj, attr_dicts)
            elif hasattr(s_data, 'atributos') and s_data.atributos:
                attr_dicts = [{"nombre": a.nombre, "valor": a.valor} for a in s_data.atributos]
                guardar_valores_stock(db, stock_obj, attr_dicts)

        # 7. IMÁGENES (S3)
        lista_mezclada = v_data.imagenes if v_data.imagenes else []
        for indice, marcador in enumerate(lista_mezclada):
            if isinstance(marcador, str) and marcador.startswith('NUEVA_'):
                key_archivo = f"file_{v_data.temp_id}_{marcador}"
                if imagenes and key_archivo in imagenes:
                    file_to_upload = imagenes[key_archivo][0]
                    # Subimos a S3 organizado por Producto/Variante
                    url_s3 = upload_image_to_s3(file_to_upload, folder=f"productos/{producto.id}/{nueva_variante.id}")
                    db.add(Imagen(url=url_s3, variante_id=nueva_variante.id, orden=indice))

    # FINALIZAR
    db.commit()
    db.refresh(producto)
    return producto



















































































# =====================================================
# LISTADO PAGINADO
# =====================================================
from sqlalchemy import func, or_, and_, cast, String, desc
from sqlalchemy.orm import Session, selectinload
from typing import List
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.stock_model import Stock
from app.models.atributo_model import Atributo, ValorAtributo

def obtener_productos_paginados(
    db: Session, 
    page: int = 1, 
    limit: int = 10,
    search: str = None, 
    tipo_busqueda: str = "todo", 
    categoria_id: int = None, 
    marca_id: int = None,
    color: str = None, 
    talla: str = None, 
    estado: str = None, 
    material: str = None, 
    precio_min: float = None, 
    precio_max: float = None,
    solo_vendidos: bool = False, 
    ordenar_por: str = "fecha_desc",
    fecha_inicio: str = None,
    fecha_fin: str = None,
    disponibilidad: str = "todos",
    proveedores_ids: List[int] = None
):
    print(f"\n🟢 [CATÁLOGO] --- INICIANDO BÚSQUEDA ---")
    print(f"🟢 [CATÁLOGO] Parámetro color recibido: '{color}'")

    offset = (page - 1) * limit
    
    query = db.query(Producto).filter(Producto.activo == True)

    necesita_join_stocks = talla or precio_min is not None or precio_max is not None or solo_vendidos or (search and tipo_busqueda == 'stock_id') or (proveedores_ids and len(proveedores_ids) > 0)
    
    if necesita_join_stocks:
        query = query.join(Producto.variantes).join(Variante.stocks)
    elif color:
        query = query.join(Producto.variantes)

    if search and search.strip():
        term = search.strip()
        if tipo_busqueda == 'producto_id' and term.isdigit():
            query = query.filter(Producto.id == int(term))
        elif tipo_busqueda == 'stock_id' and term.isdigit():
            query = query.filter(Stock.id == int(term))
        else:
            s = f"%{term}%"
            query = query.filter(or_(
                cast(Producto.id, String).ilike(s),
                Producto.sku.ilike(s),
                Producto.nombre.ilike(s)
            ))

    if categoria_id: query = query.filter(Producto.categoria_id == categoria_id)
    if marca_id: query = query.filter(Producto.marca_id == marca_id)
    if estado: query = query.filter(Producto.estado == estado)
    
    if proveedores_ids and len(proveedores_ids) > 0:
        query = query.filter(Stock.proveedor_id.in_(proveedores_ids))
    
    # ✨ FILTRO DE COLOR CON LOGS
    if color:
        c_clean = color.replace('#', '').lower()
        c_find = f"#{c_clean}"
        print(f"🟢 [CATÁLOGO] Color limpio para buscar en BD: '{c_find}'")
        
        query = query.filter(
            Producto.variantes.any(
                func.lower(Variante.hex_identidad) == c_find
            )
        )

    # ✨ LÓGICA DE DISPONIBILIDAD
    if disponibilidad == "en_stock":
        query = query.filter(Producto.variantes.any(Variante.stocks.any(Stock.cantidad > 0)))
    elif disponibilidad == "agotado":
        query = query.filter(~Producto.variantes.any(Variante.stocks.any(Stock.cantidad > 0)))
        
    if fecha_inicio: query = query.filter(Producto.fecha_registro >= fecha_inicio)
    if fecha_fin: query = query.filter(Producto.fecha_registro <= f"{fecha_fin} 23:59:59")
        
    if talla:
        query = query.join(Stock.valores).join(ValorAtributo.atributo).filter(
            and_(Atributo.nombre.ilike("talla"), ValorAtributo.valor == talla)
        )
        
    if precio_min is not None: query = query.filter(Stock.precio_venta >= precio_min)
    if precio_max is not None: query = query.filter(Stock.precio_venta <= precio_max)
    if solo_vendidos: query = query.filter(Stock.cantidad == 0)

    total = query.distinct().count()
    print(f"🟢 [CATÁLOGO] Total de productos encontrados antes de paginar: {total}")

    productos = (
        query.distinct()
        .options(
            selectinload(Producto.categoria),
            selectinload(Producto.marca),
            selectinload(Producto.variantes)
                .selectinload(Variante.stocks)
                .selectinload(Stock.valores)
                .selectinload(ValorAtributo.atributo),
            selectinload(Producto.variantes)
                .selectinload(Variante.imagenes)
        )
        .order_by(desc(Producto.id))
        .offset(offset)
        .limit(limit)
        .all()
    )

    resultados = []
    for p in productos:
        vars_activas = sorted([v for v in p.variantes if v.activo], key=lambda x: x.orden or 0)
        
        # ✨ IDENTIFICAR VARIANTE PRINCIPAL (POR COLOR)
        variante_principal = vars_activas[0] if vars_activas else None
        
        if color:
            c_target = f"#{color.replace('#', '').lower()}"
            v_match = next((v for v in vars_activas if v.hex_identidad and v.hex_identidad.lower() == c_target), None)
            if v_match:
                variante_principal = v_match
                print(f"🟢 [CATÁLOGO] Producto ID {p.id}: ¡Match de color! Usando variante ID {v_match.id}")
            else:
                print(f"🔴 [CATÁLOGO] Producto ID {p.id}: OJO, pasó el filtro de BD pero no encontré la variante en Python con color {c_target}")

        img_url = None
        if variante_principal and variante_principal.imagenes:
            img_sorted = sorted(variante_principal.imagenes, key=lambda x: x.orden or 0)
            if img_sorted:
                img_url = img_sorted[0].url
                
        if not img_url:
            for v in vars_activas:
                if v.imagenes:
                    img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
                    if img_sorted:
                        img_url = img_sorted[0].url
                        break

        stocks_activos = []
        for v in vars_activas:
            stocks_ordenados = sorted([s for s in v.stocks if s.activo], key=lambda x: x.orden or 0)
            stocks_activos.extend(stocks_ordenados)
        
        p_venta = 0.0
        p_compra = 0.0
        
        stocks_prioritarios = [s for s in variante_principal.stocks if s.activo] if variante_principal else []
        if stocks_prioritarios:
            p_venta = stocks_prioritarios[0].precio_venta
            p_compra = stocks_prioritarios[0].precio_compra
        elif stocks_activos:
            p_venta = stocks_activos[0].precio_venta
            p_compra = stocks_activos[0].precio_compra
        
        tallas_set = set()
        for s in stocks_activos:
            for val in s.valores:
                if val.atributo and val.atributo.nombre.lower() in ['talla', 'size', 'medida', 'numero', 'ml']:
                    tallas_set.add(val.valor)

        resultados.append({
            "id": p.id,
            "nombre": p.nombre,
            "fecha_registro": p.fecha_registro.isoformat() if p.fecha_registro else None,
            "fecha_actualizacion": p.fecha_actualizacion.isoformat() if p.fecha_actualizacion else None,
            "sku": p.sku,
            "tipo": p.tipo,
            "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
            "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
            "imagen": img_url,
            "stock_total": sum(s.cantidad for s in stocks_activos),
            "precio_compra": float(p_compra),
            "precio_venta": float(p_venta),
            "colores": list({v.hex_identidad for v in vars_activas if v.hex_identidad}),
            "tallas": ordenar_tallas_logicamente(tallas_set),
            "canales": {
                "web": any(s.publicar_web for s in stocks_activos),
                "vinted": any(s.publicar_vinted for s in stocks_activos),
                "wallapop": any(s.publicar_wallapop for s in stocks_activos)
            }
        })

    print(f"🟢 [CATÁLOGO] --- FIN BÚSQUEDA ---\n")
    return {"total": total, "items": resultados}









def obtener_stocks_individuales_paginados(
    db: Session, 
    page: int = 1, 
    limit: int = 10,
    search: str = None, 
    tipo_busqueda: str = "todo", 
    categoria_id: int = None, 
    marca_id: int = None,
    color: str = None, 
    talla: str = None,
    estado: str = None,
    precio_min: float = None, 
    precio_max: float = None,
    solo_vendidos: bool = False, 
    ordenar_por: str = "fecha_desc",
    fecha_inicio: str = None,
    fecha_fin: str = None,
    disponibilidad: str = "todos",
    proveedores_ids: List[int] = None
):
    print(f"\n🔵 [INVENTARIO] --- INICIANDO BÚSQUEDA ---")
    print(f"🔵 [INVENTARIO] Parámetro color recibido: '{color}'")

    offset = (page - 1) * limit
    
    query = (
        db.query(Stock)
        .join(Stock.variante)
        .join(Variante.producto)
        .filter(
            Stock.activo == True,
            Variante.activo == True,
            Producto.activo == True
        )
    )

    if search and search.strip():
        term = search.strip()
        if tipo_busqueda == 'stock_id' and term.isdigit():
            query = query.filter(Stock.id == int(term))
        elif tipo_busqueda == 'producto_id' and term.isdigit():
            query = query.filter(Producto.id == int(term))
        else:
            s = f"%{term}%"
            query = query.filter(or_(
                cast(Stock.id, String).ilike(s),
                Stock.sku.ilike(s),
                Producto.sku.ilike(s),
                Producto.nombre.ilike(s)
            ))

    if categoria_id: query = query.filter(Producto.categoria_id == categoria_id)
    if marca_id: query = query.filter(Producto.marca_id == marca_id)
    if estado: query = query.filter(Producto.estado == estado)

    if disponibilidad == "en_stock":
        query = query.filter(Stock.cantidad > 0)
    elif disponibilidad == "agotado":
        query = query.filter(Stock.cantidad == 0)
        
    if proveedores_ids and len(proveedores_ids) > 0:
        query = query.filter(Stock.proveedor_id.in_(proveedores_ids))

    # ✨ FILTRO DE COLOR CON LOGS
    if color:
        c_clean = color.replace('#', '').lower()
        c_find = f"#{c_clean}"
        print(f"🔵 [INVENTARIO] Color limpio para buscar en BD: '{c_find}'")
        query = query.filter(func.lower(Variante.hex_identidad) == c_find)

    if fecha_inicio: query = query.filter(Producto.fecha_registro >= fecha_inicio)
    if fecha_fin: query = query.filter(Producto.fecha_registro <= f"{fecha_fin} 23:59:59")
    
    if talla:
        query = query.join(Stock.valores).join(ValorAtributo.atributo).filter(
            and_(Atributo.nombre.ilike("talla"), ValorAtributo.valor == talla)
        )
        
    if precio_min is not None: query = query.filter(Stock.precio_venta >= precio_min)
    if precio_max is not None: query = query.filter(Stock.precio_venta <= precio_max)
    if solo_vendidos: query = query.filter(Stock.cantidad == 0)

    if ordenar_por == "precio_asc": query = query.order_by(Stock.precio_venta.asc())
    elif ordenar_por == "precio_desc": query = query.order_by(Stock.precio_venta.desc())
    elif ordenar_por == "stock_asc": query = query.order_by(Stock.cantidad.asc())
    elif ordenar_por == "stock_desc": query = query.order_by(Stock.cantidad.desc())
    else: query = query.order_by(Stock.id.desc())

    total = query.distinct().count()
    print(f"🔵 [INVENTARIO] Total de stocks encontrados antes de paginar: {total}")

    stocks_db = (
        query.distinct()
        .options(
            selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.categoria),
            selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.marca),
            selectinload(Stock.variante).selectinload(Variante.imagenes),
            selectinload(Stock.valores).selectinload(ValorAtributo.atributo)
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    resultados = []
    for s in stocks_db:
        v = s.variante
        p = v.producto
        
        talla_val = None
        atributos_extra = {}
        for val in s.valores:
            if val.atributo:
                nombre_attr = val.atributo.nombre.lower()
                if nombre_attr in ['talla', 'size', 'medida']:
                    talla_val = val.valor
                else:
                    atributos_extra[nombre_attr] = val.valor

        img_url = None
        if v.imagenes:
            img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
            if img_sorted:
                img_url = img_sorted[0].url

        resultados.append({
            "stock_id": s.id,
            "stock_sku": s.sku,
            "variante_id": v.id,
            "producto_id": p.id,
            "producto_nombre": p.nombre,
            "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
            "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
            "hex_identidad": v.hex_identidad,
            "identidad_variante": v.identidad_variante,
            "imagen_cover": img_url,
            "etiqueta": s.etiqueta,
            "talla": talla_val,
            "atributos_extra": atributos_extra,
            "stock_disponible": s.cantidad,
            "precio_compra": float(s.precio_compra),
            "precio_venta": float(s.precio_venta),
            "descuento": float(s.descuento or 0),
            "ubicacion_almacen": s.ubicacion,
            "canales": {
                "web": s.publicar_web,
                "vinted": s.publicar_vinted,
                "wallapop": s.publicar_wallapop
            }
        })

    print(f"🔵 [INVENTARIO] --- FIN BÚSQUEDA ---\n")
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
        "fecha_registro": producto.fecha_registro,
        "fecha_actualizacion": producto.fecha_actualizacion,
        "descripcion": producto.descripcion,
        "tipo": producto.tipo,
        "estado": producto.estado,
        "publico_objetivo": producto.publico_objetivo,
        "categoria_id": producto.categoria_id,
        "marca": producto.marca,
        "es_vintage": producto.es_vintage, 
        "epoca": producto.epoca,
        
        "variantes": [
            {
                "id": v.id,
                "hex_identidad": v.hex_identidad,
                "identidad_variante": v.identidad_variante,
                "descripcion": v.descripcion,
                "orden": v.orden,
                "imagenes": [img.url for img in sorted(v.imagenes, key=lambda x: x.orden or 0)],
                
                "stocks": [
                    {
                        "id": s.id,
                        "sku": s.sku,
                        "etiqueta": s.etiqueta,
                        "ubicacion": s.ubicacion, 
                        "cantidad": s.cantidad,
                        "precio_compra": s.precio_compra,
                        "precio_venta": s.precio_venta,
                        "descuento": s.descuento,
                        "proveedor_id": s.proveedor_id,
                        "orden": s.orden,
                        "proveedor": {"id": s.proveedor.id, "nombre_proveedor": s.proveedor.nombre_proveedor} if s.proveedor else None,
                        "publicar_web": s.publicar_web,
                        "publicar_vinted": s.publicar_vinted,
                        "publicar_wallapop": s.publicar_wallapop,
                        "fecha_compra": s.fecha_compra.isoformat() if s.fecha_compra else None,
                        "atributos": [{"nombre": val.atributo.nombre, "valor": val.valor} for val in s.valores]
                        
                    } for s in sorted([st for st in v.stocks if st.activo], key=lambda x: x.orden or 0)
                ]
                
            } for v in sorted([var for var in producto.variantes if var.activo], key=lambda x: x.orden or 0)
        ]
    }












# Asegúrate de importar esto arriba si no lo tienes para cargar el proveedor
from sqlalchemy.orm import selectinload

# =====================================================
# OBTENER DETALLE DE UN STOCK INDIVIDUAL
# =====================================================
def obtener_stock_detalle(db: Session, stock_id: int):
    # Hacemos la consulta con Eager Loading para traer las relaciones sin hacer múltiples queries
    s = (
        db.query(Stock)
        .options(
            selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.categoria),
            selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.marca),
            selectinload(Stock.variante).selectinload(Variante.imagenes),
            selectinload(Stock.valores).selectinload(ValorAtributo.atributo),
            selectinload(Stock.proveedor) # ✨ NUEVO: Le pedimos a la BD que traiga los datos del proveedor
        )
        .filter(Stock.id == stock_id)
        .first()
    )

    if not s:
        return None

    # Extraemos las entidades jerárquicas
    v = s.variante
    p = v.producto
    
    # Procesamiento de atributos (Separar talla del resto)
    talla_val = None
    atributos_extra = {}
    
    for val in s.valores:
        if val.atributo:
            nombre_attr = val.atributo.nombre.lower()
            if nombre_attr in ['talla', 'size', 'medida', 'numero']:
                talla_val = val.valor
            else:
                atributos_extra[nombre_attr] = val.valor

    # Buscar la imagen de portada de la variante
    img_url = None
    if v.imagenes:
        img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
        if img_sorted:
            img_url = img_sorted[0].url

    # Retornamos el diccionario aplanado que espera tu nuevo componente de Angular
    return {
        "stock_id": s.id,
        "stock_sku": s.sku,
        "variante_id": v.id,
        "producto_id": p.id,
        "producto_nombre": p.nombre,
        "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
        "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
        "hex_identidad": v.hex_identidad,
        "identidad_variante": v.identidad_variante,
        "imagen_cover": img_url,
        "etiqueta": s.etiqueta,
        "talla": talla_val,
        "atributos_extra": atributos_extra,
        "stock_disponible": s.cantidad,
        "precio_compra": float(s.precio_compra),
        "precio_venta": float(s.precio_venta),
        "descuento": float(s.descuento or 0),
        "ubicacion_almacen": s.ubicacion,
        
        # ✨ LOS DATOS FALTANTES QUE AHORA SÍ LLEGARÁN AL FORMULARIO:
        # Forzamos el formato YYYY-MM-DD para que Angular/HTML lo entienda
        "fecha_compra": s.fecha_compra.strftime("%Y-%m-%d") if s.fecha_compra else None,
        "proveedor_id": s.proveedor_id,
        "proveedor_nombre": s.proveedor.nombre_proveedor if s.proveedor else None,
        
        "canales": {
            "web": s.publicar_web,
            "vinted": s.publicar_vinted,
            "wallapop": s.publicar_wallapop
        }
    }












def actualizar_stock_individual(db: Session, stock_id: int, datos_nuevos: dict):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock: return None

    # Actualizamos campos directos
    if "cantidad" in datos_nuevos: stock.cantidad = datos_nuevos["cantidad"]
    if "precio_compra" in datos_nuevos: stock.precio_compra = datos_nuevos["precio_compra"]
    if "precio_venta" in datos_nuevos: stock.precio_venta = datos_nuevos["precio_venta"]
    if "descuento" in datos_nuevos: stock.descuento = datos_nuevos["descuento"]
    if "ubicacion" in datos_nuevos: stock.ubicacion = datos_nuevos["ubicacion"]
    if "fecha_compra" in datos_nuevos and datos_nuevos["fecha_compra"]: 
        stock.fecha_compra = datos_nuevos["fecha_compra"]
    
    # Switches
    if "publicar_web" in datos_nuevos: stock.publicar_web = datos_nuevos["publicar_web"]
    if "publicar_vinted" in datos_nuevos: stock.publicar_vinted = datos_nuevos["publicar_vinted"]
    if "publicar_wallapop" in datos_nuevos: stock.publicar_wallapop = datos_nuevos["publicar_wallapop"]
    
    # Proveedor
    p_id = datos_nuevos.get("proveedor_id")
    if p_id:
        stock.proveedor_id = p_id
    elif datos_nuevos.get("proveedor_nombre_nuevo"):
        nuevo_p = buscar_o_crear(db, datos_nuevos["proveedor_nombre_nuevo"])
        stock.proveedor_id = nuevo_p.id

    # ========================================================
    # 🚨 MODO PARANOIA: GUARDADO AGRESIVO DE ATRIBUTOS
    # ========================================================
    atributos_data = datos_nuevos.get("atributos")
    
    # 🕵️‍♂️ ESPÍA 1: Imprimimos en la terminal de Python lo que llegó
    print(f"\n--- INICIANDO GUARDADO DE ATRIBUTOS PARA STOCK {stock_id} ---")
    print(f"📦 DATOS RECIBIDOS DEL FRONTEND: {atributos_data}")
    
    if atributos_data is not None:
        for attr in atributos_data:
            nombre_attr = attr.get("nombre", "").strip().lower()
            valor_raw = attr.get("valor")
            
            if not nombre_attr: continue
            
            atributo_base = db.query(Atributo).filter(Atributo.nombre == nombre_attr).first()
            if not atributo_base:
                atributo_base = Atributo(nombre=nombre_attr)
                db.add(atributo_base)
                db.flush()
            
            valor_existente = next((v for v in stock.valores if v.atributo_id == atributo_base.id), None)
            
            # Si el frontend manda un valor vacío, lo borramos
            if valor_raw is None or str(valor_raw).strip() == "":
                if valor_existente:
                    print(f"🗑️ Borrando atributo: {nombre_attr}")
                    db.delete(valor_existente)
            else:
                texto_limpio = str(valor_raw).strip().upper()
                if valor_existente:
                    print(f"✏️ Actualizando {nombre_attr} -> {texto_limpio}")
                    valor_existente.valor = texto_limpio
                    db.add(valor_existente) # 🔥 FORZAMOS ACTUALIZACIÓN
                else:
                    print(f"✨ Creando nuevo {nombre_attr} -> {texto_limpio}")
                    nuevo_valor = ValorAtributo(atributo_id=atributo_base.id, valor=texto_limpio)
                    stock.valores.append(nuevo_valor)
                    db.add(nuevo_valor) # 🔥 FORZAMOS CREACIÓN

    # Guardamos todo el paquete en la Base de Datos
    db.commit()
    db.refresh(stock)
    print("✅ GUARDADO COMPLETADO\n")
    return stock





# =====================================================
# EDITAR PRODUCTO COMPLETO
# =====================================================
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
    es_vintage: bool = False,      # ✨ NUEVO
    epoca: Optional[str] = None,
    marca_id: Optional[int] = None, 
    marca_nombre: Optional[str] = None, 
    imagenes: Optional[Dict[str, List]] = None
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return None

    producto.nombre = nombre
    producto.descripcion = descripcion
    producto.categoria_id = categoria_id
    producto.tipo = tipo
    producto.estado = estado
    producto.publico_objetivo = publico_objetivo
    producto.es_vintage = es_vintage
    producto.epoca = epoca
    
    m_id = int(marca_id) if (marca_id and str(marca_id).isdigit() and int(marca_id) > 0) else None
    if m_id:
        producto.marca_id = m_id
    elif marca_nombre and marca_nombre.strip():
        nombre_clean = marca_nombre.strip()
        marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
        if marca_existente:
            producto.marca_id = marca_existente.id
        else:
            nueva_m = crear_marca(db, nombre=nombre_clean)
            producto.marca_id = nueva_m.id

    variantes_data = json.loads(variantes)
    ids_variantes_vienen = [v.get("id") for v in variantes_data if v.get("id")]
    
    for v_old in producto.variantes:
        if v_old.id not in ids_variantes_vienen:
            v_old.activo = False 

    for indice_v, v_data in enumerate(variantes_data):
        v_id = v_data.get("id")
        v_temp_id = str(v_data.get("temp_id"))
        
        if v_id:
            nv = db.query(Variante).filter(Variante.id == v_id).first()
            if nv:
                nv.hex_identidad = v_data.get("hex_identidad")
                nv.identidad_variante = v_data.get("identidad_variante")
                nv.ubicacion = v_data.get("ubicacion")
                nv.descripcion = v_data.get("descripcion")
                nv.orden = indice_v 
                nv.activo = True
        else:
            nv = Variante(
                producto_id=producto.id,
                sku="TEMP",
                hex_identidad=v_data.get("hex_identidad"),
                identidad_variante=v_data.get("identidad_variante"),
                descripcion=v_data.get("descripcion"),
                orden=indice_v 
            )
            db.add(nv)
            db.flush() 
            nv.sku = generar_sku(tipo, nv.id)

        lista_mezclada = v_data.get("imagenes", []) 
        urls_permanecen = {item.strip() for item in lista_mezclada if isinstance(item, str) and item.startswith('http')}
        
        imagenes_en_db = db.query(Imagen).filter(Imagen.variante_id == nv.id).all()
        for img_db in imagenes_en_db:
            if img_db.url.strip() not in urls_permanecen:
                try:
                    delete_image_from_s3(img_db.url)
                except: pass
                db.delete(img_db)

        for indice_img, item in enumerate(lista_mezclada):
            item_clean = item.strip() if isinstance(item, str) else item
            
            if isinstance(item_clean, str) and item_clean.startswith('http'):
                img_existente = db.query(Imagen).filter(Imagen.url == item_clean, Imagen.variante_id == nv.id).first()
                if img_existente:
                    img_existente.orden = indice_img 
            
            elif isinstance(item_clean, str) and item_clean.startswith('NUEVA_'):
                key_archivo = f"file_{v_temp_id}_{item_clean}"
                if imagenes and key_archivo in imagenes:
                    file_to_upload = imagenes[key_archivo][0]
                    url_s3 = upload_image_to_s3(file_to_upload, folder=f"productos/{producto.id}/{nv.id}")
                    db.add(Imagen(url=url_s3, variante_id=nv.id, orden=indice_img)) 

        stocks_data = v_data.get("stocks", [])
        ids_stocks_vienen = [s.get("id") for s in stocks_data if s.get("id")]
        
        db.query(Stock).filter(
            Stock.variante_id == nv.id, 
            Stock.id.notin_(ids_stocks_vienen) if ids_stocks_vienen else Stock.id > 0
        ).update({"activo": False}, synchronize_session=False)

        for indice_s, s_data in enumerate(stocks_data):
            s_id = s_data.get("id")
            
            raw_p_id = s_data.get("proveedor_id")
            p_id = int(raw_p_id) if (raw_p_id and str(raw_p_id).isdigit() and int(raw_p_id) > 0) else None

            if not p_id:
                nombre_p = s_data.get("proveedor_nombre_nuevo") or s_data.get("proveedor")
                if nombre_p and nombre_p.strip():
                    prov_obj = buscar_o_crear(db, nombre_p.strip())
                    p_id = prov_obj.id if prov_obj else None

            fecha_c = s_data.get("fecha_compra")
            if not fecha_c or fecha_c == "": fecha_c = None

            if s_id:
                so = db.query(Stock).filter(Stock.id == s_id).first()
                if so:
                    so.etiqueta = s_data.get("etiqueta")
                    so.ubicacion = s_data.get("ubicacion")
                    so.cantidad = s_data.get("cantidad", 0) or s_data.get("stock", 0)
                    so.precio_compra = s_data.get("precio_compra", 0)
                    so.precio_venta = s_data.get("precio_venta", 0)
                    so.proveedor_id = p_id 
                    so.fecha_compra = fecha_c
                    so.descuento = s_data.get("descuento", 0)
                    so.publicar_web = s_data.get("publicar_web", False)
                    so.orden = indice_s 
                    so.activo = True
            else:
                # ✨ NUEVA LÓGICA DE ID MANUAL PARA STOCKS NUEVOS EN EDICIÓN
                raw_id_manual = s_data.get("id_manual")
                id_forzado = int(raw_id_manual) if (raw_id_manual and str(raw_id_manual).isdigit() and int(raw_id_manual) > 0) else None
                
                if id_forzado:
                    stock_existente = db.query(Stock).filter(Stock.id == id_forzado).first()
                    if stock_existente:
                        raise HTTPException(status_code=400, detail=f"El ID manual {id_forzado} ya está en uso.")

                so = Stock(
                    id=id_forzado, 
                    variante_id=nv.id, 
                    proveedor_id=p_id,
                    etiqueta=s_data.get("etiqueta", "Única"),
                    ubicacion=s_data.get("ubicacion", ""),
                    cantidad=s_data.get("cantidad", 0) or s_data.get("stock", 0),
                    precio_compra=s_data.get("precio_compra", 0),
                    precio_venta=s_data.get("precio_venta", 0),
                    fecha_compra=fecha_c,
                    descuento=s_data.get("descuento", 0),
                    publicar_web=s_data.get("publicar_web", False),
                    orden=indice_s, 
                    sku="TEMP"
                )
                db.add(so)
                db.flush()
                so.sku = generar_sku(tipo, so.id)

            # ✨ ¡AQUÍ ESTÁ LA CORRECCIÓN! ✨
            # Fíjate que esto está ALINEADO con el "if s_id:" y el "else:", no dentro de ellos.
            # Así aseguramos que los atributos se actualicen SIEMPRE.
            if s_data.get("atributos"):
                guardar_valores_stock(db, so, s_data.get("atributos"))

    db.commit()
    db.refresh(producto)
    return producto















































# =====================================================
# GESTIÓN DE PAPELERA Y ELIMINACIÓN
# =====================================================
def vaciar_producto_papelera(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto:
        return {"success": False, "mensaje": "El producto no existe."}
    
    tiene_ventas = db.query(DetalleVenta).join(
        Stock, DetalleVenta.stock_id == Stock.id
    ).join(
        Variante, Stock.variante_id == Variante.id
    ).filter(
        Variante.producto_id == p_id
    ).first() is not None

    if tiene_ventas:
        return {
            "success": False, 
            "mensaje": "⚠️ No puedes destruir este producto porque tiene ventas registradas. Mantenlo en la papelera."
        }
    
    print(f"🧹 Iniciando borrado permanente del producto {p_id}...")
    for variante in producto.variantes:
        for img in getattr(variante, 'imagenes', []):
            try: 
                delete_image_from_s3(img.url) 
                print(f"✅ S3: Imagen borrada -> {img.url}")
            except Exception as e: 
                print(f"⚠️ Error S3: {e}")
    
    db.delete(producto)
    db.commit()
    
    return {"success": True, "mensaje": "✅ Producto eliminado permanentemente."}

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

def obtener_productos_papelera(db: Session, page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    
    # 🔍 FILTRO INTELIGENTE: Traemos el producto si él está inactivo 
    # O si tiene alguna variante inactiva O si tiene algún stock inactivo.
    query = (
        db.query(Producto)
        .filter(
            or_(
                Producto.activo == False,
                Producto.variantes.any(Variante.activo == False),
                Producto.variantes.any(Variante.stocks.any(Stock.activo == False))
            )
        )
        .options(
            joinedload(Producto.categoria),
            joinedload(Producto.marca),
            joinedload(Producto.variantes).joinedload(Variante.stocks),
            joinedload(Producto.variantes).joinedload(Variante.imagenes)
        )
        .order_by(Producto.id.desc())
    )

    total = query.distinct().count()
    productos = query.distinct().offset(offset).limit(limit).all()

    resultados = []
    for p in productos:
        # --- FILTRADO DE SEGURIDAD PARA LA VISTA ---
        # Solo queremos mostrar en la papelera las ramas que de verdad están "muertas"
        vars_finales = []
        
        for v in p.variantes:
            # Si la variante está inactiva, la metemos con todos sus stocks borrados
            # Si la variante está activa pero tiene stocks inactivos, también la metemos
            stocks_borrados = [s for s in v.stocks if s.activo == False]
            
            if v.activo == False or len(stocks_borrados) > 0:
                vars_finales.append({
                    "id": v.id,
                    "identidad_variante": v.identidad_variante,
                    "hex_identidad": v.hex_identidad,
                    "descripcion": v.descripcion,
                    "activo": v.activo,
                    "stocks": [
                        {
                            "id": s.id,
                            "sku": s.sku,
                            "etiqueta": s.etiqueta,
                            "cantidad": s.cantidad,
                            "precio_venta": s.precio_venta,
                            "ubicacion": s.ubicacion,
                            "activo": s.activo
                        } for s in (v.stocks if v.activo == False else stocks_borrados)
                    ]
                })

        # Cálculos para la fila principal (solo de lo que está en la papelera)
        stock_oculto = sum(s['cantidad'] for v in vars_finales for s in v['stocks'])
        precios_ocultos = [s['precio_venta'] for v in vars_finales for s in v['stocks']]
        
        imagen_cover = None
        if p.variantes:
            v_con_img = next((v for v in p.variantes if v.imagenes), None)
            if v_con_img:
                img_sorted = sorted(v_con_img.imagenes, key=lambda x: x.orden or 0)
                if img_sorted:
                    imagen_cover = img_sorted[0].url

        resultados.append({
            "id": p.id,
            "nombre": p.nombre,
            "sku": p.sku,
            "tipo": p.tipo,
            "activo": p.activo, # Importante para que el Front sepa si el padre está borrado
            "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
            "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
            "imagen": imagen_cover,
            "stock_total": stock_oculto,
            "precio_min": min(precios_ocultos) if precios_ocultos else 0,
            "precio_max": max(precios_ocultos) if precios_ocultos else 0,
            "colores": list({v.hex_identidad for v in p.variantes if v.hex_identidad}),
            "variantes": vars_finales # ✨ AQUÍ ESTÁ LA DATA ANIDADA PARA EL ACORDEÓN
        })

    return {"total": total, "items": resultados}

from app.services.s3_service import delete_image_from_s3
from app.models.ventas_model import DetalleVenta
from sqlalchemy.orm import Session

# =====================================================
# HELPER: OPTIMIZADOR S3 PARA PAPELERA 🧹
# =====================================================
def optimizar_imagenes_variante(db: Session, variante: Variante):
    """
    Mantiene solo 1 foto (la de portada) en S3 y BD. Borra el resto.
    Ideal para ahorrar costos cuando algo va a la papelera.
    """
    if not variante.imagenes: return
    
    # Ordenamos para asegurar que la [0] es la portada
    imagenes_ordenadas = sorted(variante.imagenes, key=lambda x: x.orden or 0)
    
    # Si hay más de 1 imagen, destruimos las extra
    if len(imagenes_ordenadas) > 1:
        imagenes_a_borrar = imagenes_ordenadas[1:]
        for img in imagenes_a_borrar:
            try:
                delete_image_from_s3(img.url)
                print(f"✅ S3 Optimizado: Imagen secundaria borrada -> {img.url}")
            except Exception as e:
                print(f"⚠️ Error S3: {e}")
            db.delete(img) # Borramos de la BD
        db.flush()

# =====================================================
# MOVER A PAPELERA (SOFT DELETE + APAGÓN DE CANALES)
# =====================================================
def mover_producto_papelera(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: return {"success": False, "mensaje": "Producto no encontrado."}
    
    producto.activo = False
    for v in producto.variantes:
        v.activo = False
        optimizar_imagenes_variante(db, v) # Limpieza S3
        
        for s in v.stocks:
            s.activo = False
            # 🔌 APAGÓN DE CANALES DE VENTA
            s.publicar_web = False
            s.publicar_vinted = False
            s.publicar_wallapop = False
            
    db.commit()
    return {"success": True, "mensaje": "🗑️ Producto a papelera y canales desconectados."}

def mover_variante_papelera(db: Session, v_id: int):
    variante = db.query(Variante).filter(Variante.id == v_id).first()
    if not variante: return {"success": False, "mensaje": "Variante no encontrada."}
    
    variante.activo = False
    optimizar_imagenes_variante(db, variante) # Limpieza S3
    
    for s in variante.stocks:
        s.activo = False
        # 🔌 APAGÓN DE CANALES DE VENTA
        s.publicar_web = False
        s.publicar_vinted = False
        s.publicar_wallapop = False
        
    db.commit()
    return {"success": True, "mensaje": "🗑️ Variante a papelera y canales desconectados."}

def mover_stock_papelera(db: Session, s_id: int):
    stock = db.query(Stock).filter(Stock.id == s_id).first()
    if not stock: return {"success": False, "mensaje": "Stock no encontrado."}
    
    stock.activo = False
    # 🔌 APAGÓN DE CANALES DE VENTA
    stock.publicar_web = False
    stock.publicar_vinted = False
    stock.publicar_wallapop = False
    
    db.commit()
    return {"success": True, "mensaje": "🗑️ Talla movida a la papelera y desconectada."}

# =====================================================
# RESTAURAR DE PAPELERA
# =====================================================
def restaurar_producto_papelera(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: return {"success": False, "mensaje": "No encontrado."}
    
    producto.activo = True # Despierta el producto
    
    # ✨ CASCADA DE RESTAURACIÓN TOTAL (Revive todo)
    for v in producto.variantes:
        v.activo = True
        for s in v.stocks:
            s.activo = True
            
            # 🛡️ EL SEGURO ANTI-FANTASMAS Y ANTI-ERRORES
            # Apagamos los canales de venta. Así el producto vuelve a tu panel
            # completo con todas sus tallas, pero como "Borrador" oculto al público.
            s.publicar_web = False
            s.publicar_vinted = False
            s.publicar_wallapop = False

    db.commit()
    return {"success": True, "mensaje": "♻️ Producto restaurado por completo (Modo Borrador oculto en web)."}

def restaurar_variante_papelera(db: Session, v_id: int):
    variante = db.query(Variante).filter(Variante.id == v_id).first()
    if not variante: return {"success": False, "mensaje": "No encontrado."}
    variante.activo = True
    variante.producto.activo = True # Obligamos al padre a despertar
    db.commit()
    return {"success": True, "mensaje": "♻️ Variante restaurada."}

def restaurar_stock_papelera(db: Session, s_id: int):
    stock = db.query(Stock).filter(Stock.id == s_id).first()
    if not stock: return {"success": False, "mensaje": "No encontrado."}
    stock.activo = True
    stock.variante.activo = True # Obligamos al padre a despertar
    stock.variante.producto.activo = True # Obligamos al abuelo a despertar
    db.commit()
    return {"success": True, "mensaje": "♻️ Talla/Medida restaurada."}

# =====================================================
# DESTRUCCIÓN TOTAL (HARD DELETE) CON VALIDACIÓN
# =====================================================
def destruir_producto_total(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: return {"success": False, "mensaje": "No existe."}
    
    # 🛡️ EL ESCUDO CONTRA HACKERS DE HTML
    if producto.activo == True:
        return {"success": False, "mensaje": "⚠️ Violación de seguridad: No puedes destruir un producto que está activo. Debes enviarlo a la papelera primero."}
    
    # 1. Validación estricta: ¿Se ha vendido algo de esto?
    ventas = db.query(DetalleVenta).join(Stock).join(Variante).filter(Variante.producto_id == p_id).first()
    if ventas:
        return {"success": False, "mensaje": "⛔ No puedes destruir este producto porque está asociado a facturas/ventas."}

    # 2. Si no hay ventas, aniquilamos S3
    for v in producto.variantes:
        for img in v.imagenes:
            try: delete_image_from_s3(img.url)
            except: pass

    # 3. Borrado en BD (El cascade="all, delete" borrará todo hacia abajo)
    db.delete(producto)
    db.commit()
    return {"success": True, "mensaje": "✅ Producto y derivados eliminados de la existencia."}

def destruir_variante_total(db: Session, v_id: int):
    variante = db.query(Variante).filter(Variante.id == v_id).first()
    if not variante: return {"success": False, "mensaje": "No existe."}
    
    # 🛡️ EL ESCUDO CONTRA HACKERS DE HTML
    if variante.activo == True:
        return {"success": False, "mensaje": "⚠️ Violación de seguridad: No puedes destruir una variante activa."}
    
    ventas = db.query(DetalleVenta).join(Stock).filter(Stock.variante_id == v_id).first()
    if ventas:
        return {"success": False, "mensaje": "⛔ No puedes destruir esta variante porque tiene tallas vendidas."}

    for img in variante.imagenes:
        try: delete_image_from_s3(img.url)
        except: pass

    db.delete(variante)
    db.commit()
    return {"success": True, "mensaje": "✅ Variante eliminada de la existencia."}

def destruir_stock_total(db: Session, s_id: int):
    stock = db.query(Stock).filter(Stock.id == s_id).first()
    if not stock: return {"success": False, "mensaje": "No existe."}
    
    # 🛡️ EL ESCUDO CONTRA HACKERS DE HTML
    if stock.activo == True:
        return {"success": False, "mensaje": "⚠️ Violación de seguridad: No puedes destruir un stock activo."}
    
    ventas = db.query(DetalleVenta).filter(DetalleVenta.stock_id == s_id).first()
    if ventas:
        return {"success": False, "mensaje": "⛔ No puedes destruir esta talla porque se registró en una venta."}

    db.delete(stock)
    db.commit()
    return {"success": True, "mensaje": "✅ Talla eliminada de la existencia."}