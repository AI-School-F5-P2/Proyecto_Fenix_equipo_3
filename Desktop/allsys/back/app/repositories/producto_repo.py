



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
def crear_producto(
    db: Session, nombre: str, estado: str, descripcion: Optional[str], categoria_id: int, tipo: str, 
    publico_objetivo: str, variantes: str, marca_id: Optional[int] = None, 
    marca_nombre: Optional[str] = None, imagenes: Optional[Dict[str, List]] = None
):
    desc_final = descripcion.strip() if descripcion else ""
    
    if not publico_objetivo or not publico_objetivo.strip():
        raise HTTPException(status_code=400, detail="El público objetivo es obligatorio.")

    try:
        variantes_json = json.loads(variantes)
        variantes_validadas = [VarianteSchema(**v) for v in variantes_json] 
    except ValidationError as e:
        error_msg = e.errors()[0].get("msg", "Datos de variante inválidos")
        raise HTTPException(status_code=400, detail=f"Error en variantes: {error_msg}")

    if not marca_id and marca_nombre:
        nombre_clean = marca_nombre.strip()
        marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
        marca_id = marca_existente.id if marca_existente else crear_marca(db, nombre=nombre_clean).id

    producto = Producto(
        nombre=nombre.strip(), 
        descripcion=desc_final, 
        categoria_id=categoria_id,
        marca_id=marca_id, 
        estado=estado,
        tipo=tipo, 
        publico_objetivo=publico_objetivo,
        sku="TEMP"
    )
    db.add(producto)
    db.flush()
    producto.sku = generar_sku(tipo, producto.id)

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

        for s_data in v_data.stocks:
            if s_data.stock <= 0:
                raise HTTPException(status_code=400, detail="El stock debe ser mayor a 0.")

            p_id = s_data.proveedor_id
            if not p_id:
                nombre_p = s_data.proveedor_nombre_nuevo or s_data.proveedor
                proveedor_obj = buscar_o_crear(db, nombre_p)
                p_id = proveedor_obj.id if proveedor_obj else None

            id_forzado = s_data.id_manual if hasattr(s_data, 'id_manual') and s_data.id_manual else None

            # Verificación de seguridad: Si envías un ID, comprobamos que no esté ocupado
            if id_forzado:
                stock_existente = db.query(Stock).filter(Stock.id == id_forzado).first()
                if stock_existente:
                    raise HTTPException(status_code=400, detail=f"El ID manual {id_forzado} ya está en uso en otro producto.")

            stock_obj = Stock(
                id=id_forzado, # ✨ AQUÍ LE PASAMOS EL ID FORZADO (Si es None, PostgreSQL usará el Auto-Increment)
                variante_id=nueva_variante.id,
                proveedor_id=p_id,
                ubicacion=s_data.ubicacion,
                etiqueta=s_data.etiqueta,
                cantidad=s_data.stock,
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

        lista_mezclada = v_data.imagenes if v_data.imagenes else []
        for indice, marcador in enumerate(lista_mezclada):
            if isinstance(marcador, str) and marcador.startswith('NUEVA_'):
                key_archivo = f"file_{v_data.temp_id}_{marcador}"
                if imagenes and key_archivo in imagenes:
                    file_to_upload = imagenes[key_archivo][0]
                    url_s3 = upload_image_to_s3(file_to_upload, folder=f"productos/{producto.id}/{nueva_variante.id}")
                    db.add(Imagen(url=url_s3, variante_id=nueva_variante.id, orden=indice))

    db.commit()
    db.refresh(producto)
    return producto

# =====================================================
# LISTADO PAGINADO
# =====================================================
from sqlalchemy import or_, and_, cast, String, desc
from sqlalchemy.orm import Session, selectinload
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
    proveedores_ids: List[int] = None
):
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
    
    if color:
        color_clean = color.strip()
        if not color_clean.startswith('#'):
            color_clean = f"#{color_clean}"
        query = query.filter(Variante.hex_identidad.ilike(color_clean))

    if fecha_inicio: 
        query = query.filter(Producto.created_at >= fecha_inicio) 
    if fecha_fin: 
        query = query.filter(Producto.created_at <= f"{fecha_fin} 23:59:59")
        
    if talla:
        query = query.join(Stock.valores).join(ValorAtributo.atributo).filter(
            and_(Atributo.nombre.ilike("talla"), ValorAtributo.valor == talla)
        )
    if precio_min is not None: query = query.filter(Stock.precio_venta >= precio_min)
    if precio_max is not None: query = query.filter(Stock.precio_venta <= precio_max)
    if solo_vendidos: query = query.filter(Stock.cantidad == 0)

    total = query.distinct().count()

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
        
        stocks_activos = []
        for v in vars_activas:
            stocks_ordenados = sorted([s for s in v.stocks if s.activo], key=lambda x: x.orden or 0)
            stocks_activos.extend(stocks_ordenados)
        
        p_venta = stocks_activos[0].precio_venta if stocks_activos else 0.0
        p_compra = stocks_activos[0].precio_compra if stocks_activos else 0.0
        
        # Recolectamos las tallas sin repetidos
        tallas_set = set()
        for s in stocks_activos:
            for val in s.valores:
                if val.atributo and val.atributo.nombre.lower() in ['talla', 'size', 'medida', 'numero', 'ml']:
                    tallas_set.add(val.valor)

        img_url = None
        for v in vars_activas:
            if v.imagenes:
                img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
                if img_sorted:
                    img_url = img_sorted[0].url
                    break

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
            
            # ✨ AQUÍ SE APLICA EL ORDENADOR INTELIGENTE
            "tallas": ordenar_tallas_logicamente(tallas_set),
            
            "canales": {
                "web": any(s.publicar_web for s in stocks_activos),
                "vinted": any(s.publicar_vinted for s in stocks_activos),
                "wallapop": any(s.publicar_wallapop for s in stocks_activos)
            }
        })

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
    proveedores_ids: List[int] = None
):
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
    
    if proveedores_ids and len(proveedores_ids) > 0:
        query = query.filter(Stock.proveedor_id.in_(proveedores_ids))

    if color:
        color_clean = color.strip()
        if not color_clean.startswith('#'):
            color_clean = f"#{color_clean}"
        query = query.filter(Variante.hex_identidad.ilike(color_clean))

    if fecha_inicio: 
        query = query.filter(Producto.created_at >= fecha_inicio)
    if fecha_fin: 
        query = query.filter(Producto.created_at <= f"{fecha_fin} 23:59:59")
    
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
                so = Stock(
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


def obtener_productos_papelera(db: Session, page: int = 1, limit: int = 10):
    offset = (page - 1) * limit
    
    query = (
        db.query(Producto)
        .filter(Producto.activo == False)
        .options(
            joinedload(Producto.categoria),
            joinedload(Producto.marca),
            joinedload(Producto.variantes).joinedload(Variante.stocks),
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
        
        imagen_cover = None
        if p.variantes:
            variante_principal = next((v for v in p.variantes if v.imagenes), None)
            if variante_principal:
                imagenes_ordenadas = sorted(variante_principal.imagenes, key=lambda img: img.orden or 0)
                if imagenes_ordenadas:
                    imagen_cover = imagenes_ordenadas[0].url

        colores_unicos = list({v.hex_identidad for v in p.variantes if v.hex_identidad})
        
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
                "web": False, 
                "vinted": False,
                "wallapop": False
            }
        })

    return {"total": total, "items": resultados}


def mover_a_papelera(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: return False
    
    producto.activo = False 
    
    db.commit()
    return {"success": True, "mensaje": "🗑️ Producto movido a la papelera."}


def restaurar_de_papelera(db: Session, p_id: int):
    producto = db.query(Producto).filter(Producto.id == p_id).first()
    if not producto: return False
    
    producto.activo = True
    
    db.commit()
    return {"success": True, "mensaje": "♻️ Producto restaurado con éxito."}
























# import json
# import random
# import string
# from typing import Dict, List, Optional
# from fastapi import HTTPException # Añadimos esto para lanzar errores
# from pydantic import ValidationError # Añadimos esto
# from sqlalchemy.orm import Session, joinedload
# from app.models.variantes_model import Variante
# from app.models.stock_model import Stock
# from app.models.atributo_model import Atributo, ValorAtributo
# from app.models.marcas_model import Marca
# from app.models.variante_imagen_model import Imagen
# from app.schemas.variante_schema import VarianteSchema
# from app.services.s3_service import delete_image_from_s3, upload_image_to_s3
# from app.repositories.proveedores_repo import buscar_o_crear
# from app.repositories.marcas_repo import crear_marca
# from app.models.producto_model import Producto



# from app.models.ventas_model import DetalleVenta 

# # =====================================================
# # SKU GENERATOR
# # =====================================================
# def generar_sku(tipo: str, id_unico: int) -> str:
#     prefijo = tipo[:3].upper() if tipo else "GEN"
#     rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#     return f"{prefijo}-{rand}-{id_unico}"

# # =====================================================
# # HELPERS: VALORES DE ATRIBUTOS (EAV)
# # =====================================================
# def guardar_valores_stock(db: Session, stock_obj: Stock, atributos_data: list):
#     db.query(ValorAtributo).filter_by(stock_id=stock_obj.id).delete()
#     for attr in atributos_data:
#         if not attr.get("valor"): continue 

#         nombre_attr = attr["nombre"].strip().lower()
#         atributo_base = db.query(Atributo).filter(Atributo.nombre == nombre_attr).first()
        
#         if not atributo_base:
#             atributo_base = Atributo(nombre=nombre_attr)
#             db.add(atributo_base)
#             db.flush()

#         nuevo_valor = ValorAtributo(
#             stock_id=stock_obj.id,
#             atributo_id=atributo_base.id,
#             valor=str(attr["valor"]).strip()
#         )
#         db.add(nuevo_valor)

# # =====================================================
# # CREAR PRODUCTO COMPLETO
# # =====================================================
# # app/repositories/producto_repo.py

# def crear_producto(
#     db: Session, nombre: str, estado: str, descripcion: Optional[str], categoria_id: int, tipo: str, 
#     publico_objetivo: str, variantes: str, marca_id: Optional[int] = None, 
#     marca_nombre: Optional[str] = None, imagenes: Optional[Dict[str, List]] = None
# ):
#     # 1. Validaciones Generales relativas
#     # ✨ LA DESCRIPCIÓN YA NO ES OBLIGATORIA AQUÍ
#     desc_final = descripcion.strip() if descripcion else ""
    
#     if not publico_objetivo or not publico_objetivo.strip():
#         raise HTTPException(status_code=400, detail="El público objetivo es obligatorio.")

#     # 2. Validar JSON de variantes
#     try:
#         variantes_json = json.loads(variantes)
#         variantes_validadas = [VarianteSchema(**v) for v in variantes_json] 
#     except ValidationError as e:
#         error_msg = e.errors()[0].get("msg", "Datos de variante inválidos")
#         raise HTTPException(status_code=400, detail=f"Error en variantes: {error_msg}")

#     # 3. Lógica de Marca
#     if not marca_id and marca_nombre:
#         nombre_clean = marca_nombre.strip()
#         marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
#         marca_id = marca_existente.id if marca_existente else crear_marca(db, nombre=nombre_clean).id

#     # 4. Crear Producto
#     producto = Producto(
#         nombre=nombre.strip(), 
#         descripcion=desc_final, 
#         categoria_id=categoria_id,
#         marca_id=marca_id, 
#         estado=estado,         # ✨ ASEGÚRATE QUE EN TU MODELO SEA 'estado'
#         tipo=tipo, 
#         publico_objetivo=publico_objetivo,
#         sku="TEMP"
#     )
#     db.add(producto)
#     db.flush()
#     producto.sku = generar_sku(tipo, producto.id)

#     # 5. Bucle de Variantes
#     for v_data in variantes_validadas:
#         # ✨ REGLA: Descripción de variante OBLIGATORIA
#         if not v_data.descripcion or not v_data.descripcion.strip():
#             raise HTTPException(status_code=400, detail="Cada variante debe tener su propia descripción.")

#         nueva_variante = Variante(
#             producto_id=producto.id,
#             sku="TEMP",
#             hex_identidad=v_data.hex_identidad,           
#             identidad_variante=v_data.identidad_variante, 
#             descripcion=v_data.descripcion.strip() # ✨ Guardamos la desc de la variante
#         )
#         db.add(nueva_variante)
#         db.flush()
#         nueva_variante.sku = generar_sku(tipo, nueva_variante.id)

#         for s_data in v_data.stocks:
#             # ✨ REGLA: Stock debe ser > 0
#             if s_data.stock <= 0:
#                 raise HTTPException(status_code=400, detail="El stock debe ser mayor a 0.")

#             p_id = s_data.proveedor_id
#             if not p_id:
#                 nombre_p = s_data.proveedor_nombre_nuevo or s_data.proveedor
#                 proveedor_obj = buscar_o_crear(db, nombre_p)
#                 p_id = proveedor_obj.id if proveedor_obj else None

#             stock_obj = Stock(
#                 variante_id=nueva_variante.id,
#                 proveedor_id=p_id,
#                 ubicacion=s_data.ubicacion,
#                 etiqueta=s_data.etiqueta,
#                 cantidad=s_data.stock, # Mapeamos 'stock' del JSON a 'cantidad' en DB
#                 precio_compra=s_data.precio_compra,
#                 precio_venta=s_data.precio_venta,
#                 fecha_compra=s_data.fecha_compra,
#                 publicar_web=s_data.publicar_web,
#                 publicar_vinted=s_data.publicar_vinted,
#                 publicar_wallapop=s_data.publicar_wallapop,
#                 sku="TEMP"
#             )
#             db.add(stock_obj)
#             db.flush()
#             stock_obj.sku = generar_sku(tipo, stock_obj.id)

#             if s_data.atributos:
#                 attr_dicts = [{"nombre": a.nombre, "valor": a.valor} for a in s_data.atributos]
#                 guardar_valores_stock(db, stock_obj, attr_dicts)

#         # Imágenes
#         lista_mezclada = v_data.imagenes if v_data.imagenes else []
#         for indice, marcador in enumerate(lista_mezclada):
#             if isinstance(marcador, str) and marcador.startswith('NUEVA_'):
#                 # La clave enviada por Angular es "file_{temp_id}_{marcador}"
#                 key_archivo = f"file_{v_data.temp_id}_{marcador}"
#                 if imagenes and key_archivo in imagenes:
#                     file_to_upload = imagenes[key_archivo][0]
#                     url_s3 = upload_image_to_s3(file_to_upload, folder=f"productos/{producto.id}/{nueva_variante.id}")
#                     db.add(Imagen(url=url_s3, variante_id=nueva_variante.id, orden=indice))

#     db.commit()
#     db.refresh(producto)
#     return producto

# # =====================================================
# # LISTADO PAGINADO
# # =====================================================
# from sqlalchemy import or_, and_, cast, String, desc
# from sqlalchemy.orm import Session, selectinload
# from app.models.producto_model import Producto
# from app.models.variantes_model import Variante
# from app.models.stock_model import Stock
# from app.models.atributo_model import Atributo, ValorAtributo










































# def obtener_productos_paginados(
#     db: Session, 
#     page: int = 1, 
#     limit: int = 10,
#     search: str = None, 
#     tipo_busqueda: str = "todo", 
#     categoria_id: int = None, 
#     marca_id: int = None,
#     color: str = None, 
#     talla: str = None, 
#     estado: str = None, 
#     material: str = None, 
#     precio_min: float = None, 
#     precio_max: float = None,
#     solo_vendidos: bool = False, 
#     ordenar_por: str = "fecha_desc",
#     fecha_inicio: str = None, # ✨ NUEVO
#     fecha_fin: str = None,
#     proveedores_ids: List[int] = None # ✨ NUEVO PARÁMETRO
# ):
#     offset = (page - 1) * limit
    
#     # 1. Filtramos primero (Query base)
#     query = db.query(Producto).filter(Producto.activo == True)

#     # 2. Análisis inteligente de JOINs
#     # ✨ ACTUALIZADO: Si busca por proveedor, OBLIGAMOS a unir la tabla de stocks
#     necesita_join_stocks = talla or precio_min is not None or precio_max is not None or solo_vendidos or (search and tipo_busqueda == 'stock_id') or (proveedores_ids and len(proveedores_ids) > 0)

#     if necesita_join_stocks:
#         query = query.join(Producto.variantes).join(Variante.stocks)
#     elif color:
#         query = query.join(Producto.variantes)

#     # 3. Aplicación de filtros (Buscador)
#     if search and search.strip():
#         term = search.strip()
#         if tipo_busqueda == 'producto_id' and term.isdigit():
#             query = query.filter(Producto.id == int(term))
#         elif tipo_busqueda == 'stock_id' and term.isdigit():
#             query = query.filter(Stock.id == int(term))
#         else:
#             s = f"%{term}%"
#             query = query.filter(or_(
#                 cast(Producto.id, String).ilike(s),
#                 Producto.sku.ilike(s),
#                 Producto.nombre.ilike(s)
#             ))

#     # 4. Filtros Normales
#     if categoria_id: query = query.filter(Producto.categoria_id == categoria_id)
#     if marca_id: query = query.filter(Producto.marca_id == marca_id)
#     if estado: query = query.filter(Producto.estado == estado)
    
#     # ✨ NUEVO FILTRO MULTIPLE DE PROVEEDOR
#     if proveedores_ids and len(proveedores_ids) > 0:
#         query = query.filter(Stock.proveedor_id.in_(proveedores_ids))
    
#     if color:
#         color_clean = color.strip()
#         if not color_clean.startswith('#'):
#             color_clean = f"#{color_clean}"
#         query = query.filter(Variante.hex_identidad.ilike(color_clean))

#     if fecha_inicio: 
#         query = query.filter(Producto.created_at >= fecha_inicio) # ✨ Filtra por Producto
#     if fecha_fin: 
#         # Añadimos ' 23:59:59' para incluir todo el día final
#         query = query.filter(Producto.created_at <= f"{fecha_fin} 23:59:59")
        
#     if talla:
#         query = query.join(Stock.valores).join(ValorAtributo.atributo).filter(
#             and_(Atributo.nombre.ilike("talla"), ValorAtributo.valor == talla)
#         )
#     if precio_min is not None: query = query.filter(Stock.precio_venta >= precio_min)
#     if precio_max is not None: query = query.filter(Stock.precio_venta <= precio_max)
#     if solo_vendidos: query = query.filter(Stock.cantidad == 0)

#     # 5. Conteo total
#     total = query.distinct().count()

#     # 6. Carga optimizada
#     productos = (
#         query.distinct()
#         .options(
#             selectinload(Producto.categoria),
#             selectinload(Producto.marca),
#             selectinload(Producto.variantes)
#                 .selectinload(Variante.stocks)
#                 .selectinload(Stock.valores)
#                 .selectinload(ValorAtributo.atributo),
#             selectinload(Producto.variantes)
#                 .selectinload(Variante.imagenes)
#         )
#         .order_by(desc(Producto.id))
#         .offset(offset)
#         .limit(limit)
#         .all()
#     )

#     # 7. Construcción manual de resultados
#     resultados = []
#     for p in productos:
#         # ✨ 1. ORDENAMOS LAS VARIANTES POR SU CAMPO ORDEN (Para que la "portada" sea la que dejaste de primera)
#         vars_activas = sorted([v for v in p.variantes if v.activo], key=lambda x: x.orden or 0)
        
#         # ✨ 2. OBTENEMOS LOS STOCKS (Basados en las variantes ya ordenadas)
#         stocks_activos = []
#         for v in vars_activas:
#             # Los stocks dentro de la variante también los ordenamos por si acaso
#             stocks_ordenados = sorted([s for s in v.stocks if s.activo], key=lambda x: x.orden or 0)
#             stocks_activos.extend(stocks_ordenados)
        
#         # Obtenemos precio de la variante principal (o la primera que tenga stock)
#         p_venta = stocks_activos[0].precio_venta if stocks_activos else 0.0
#         p_compra = stocks_activos[0].precio_compra if stocks_activos else 0.0
        
#         tallas_set = set()
#         for s in stocks_activos:
#             for val in s.valores:
#                 if val.atributo and val.atributo.nombre.lower() in ['talla', 'size']:
#                     tallas_set.add(val.valor)

#         # ✨ 3. BUSCAMOS LA IMAGEN DE PORTADA
#         img_url = None
#         # Como vars_activas ya está ordenada, el primer for buscará en la variante "Portada"
#         for v in vars_activas:
#             if v.imagenes:
#                 # Nos aseguramos de coger la imagen "Portada" dentro de esa variante
#                 img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
#                 if img_sorted:
#                     img_url = img_sorted[0].url
#                     break # Encontramos la imagen principal, dejamos de buscar

#         # ✨ ELIMINAMOS EL SET Y USAMOS UNA LISTA PARA MANTENER TU ORDEN
#         tallas_lista = []
#         for s in stocks_activos:
#             for val in s.valores:
#                 if val.atributo and val.atributo.nombre.lower() in ['talla', 'size']:
#                     # Solo la añadimos si no está ya en la lista, 
#                     # así evitamos repetidas pero conservamos tu orden manual
#                     if val.valor not in tallas_lista:
#                         tallas_lista.append(val.valor)

#         resultados.append({
#             "id": p.id,
#             "nombre": p.nombre,
#             "fecha_registro": p.fecha_registro.isoformat() if p.fecha_registro else None,
#             "fecha_actualizacion": p.fecha_actualizacion.isoformat() if p.fecha_actualizacion else None,
#             "sku": p.sku,
#             "tipo": p.tipo,
#             "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
#             "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
#             "imagen": img_url,
#             "stock_total": sum(s.cantidad for s in stocks_activos),
#             "precio_compra": float(p_compra),
#             "precio_venta": float(p_venta),
            
#             # Dejamos que los colores se mantengan únicos sin importar el orden
#             "colores": list({v.hex_identidad for v in vars_activas if v.hex_identidad}),
#             "tallas": tallas_lista,
#             "canales": {
#                 "web": any(s.publicar_web for s in stocks_activos),
#                 "vinted": any(s.publicar_vinted for s in stocks_activos),
#                 "wallapop": any(s.publicar_wallapop for s in stocks_activos)
#             }
#         })

#     return {"total": total, "items": resultados}


# # ==========================================================================================================
# # ==========================================================================================================
# # ==========================================================================================================
# # ==========================================================================================================

# def obtener_stocks_individuales_paginados(
#     db: Session, 
#     page: int = 1, 
#     limit: int = 10,
#     search: str = None, 
#     tipo_busqueda: str = "todo", 
#     categoria_id: int = None, 
#     marca_id: int = None,
#     color: str = None, 
#     talla: str = None,
#     estado: str = None,
#     precio_min: float = None, 
#     precio_max: float = None,
#     solo_vendidos: bool = False, 
#     ordenar_por: str = "fecha_desc",
#     fecha_inicio: str = None, # ✨ NUEVO
#     fecha_fin: str = None,
#     proveedores_ids: List[int] = None # ✨ NUEVO PARÁMETRO
# ):
#     offset = (page - 1) * limit
    
#     # 1. LA CONSULTA BASE
#     query = (
#         db.query(Stock)
#         .join(Stock.variante)
#         .join(Variante.producto)
#         .filter(
#             Stock.activo == True,
#             Variante.activo == True,
#             Producto.activo == True
#         )
#     )

#     # 2. APLICACIÓN DE FILTROS DE BÚSQUEDA
#     if search and search.strip():
#         term = search.strip()
#         if tipo_busqueda == 'stock_id' and term.isdigit():
#             query = query.filter(Stock.id == int(term))
#         elif tipo_busqueda == 'producto_id' and term.isdigit():
#             query = query.filter(Producto.id == int(term))
#         else:
#             s = f"%{term}%"
#             query = query.filter(or_(
#                 cast(Stock.id, String).ilike(s),
#                 Stock.sku.ilike(s),
#                 Producto.sku.ilike(s),
#                 Producto.nombre.ilike(s)
#             ))

#     # 3. Filtros Normales
#     if categoria_id: query = query.filter(Producto.categoria_id == categoria_id)
#     if marca_id: query = query.filter(Producto.marca_id == marca_id)
#     if estado: query = query.filter(Producto.estado == estado)
    
#     # ✨ NUEVO FILTRO MULTIPLE DE PROVEEDOR
#     if proveedores_ids and len(proveedores_ids) > 0:
#         query = query.filter(Stock.proveedor_id.in_(proveedores_ids))

#     if color:
#         color_clean = color.strip()
#         if not color_clean.startswith('#'):
#             color_clean = f"#{color_clean}"
#         query = query.filter(Variante.hex_identidad.ilike(color_clean))

#     if fecha_inicio: 
#         query = query.filter(Producto.created_at >= fecha_inicio) # ✨ Filtra por Producto
#     if fecha_fin: 
#         # Añadimos ' 23:59:59' para incluir todo el día final
#         query = query.filter(Producto.created_at <= f"{fecha_fin} 23:59:59")
    
#     if talla:
#         query = query.join(Stock.valores).join(ValorAtributo.atributo).filter(
#             and_(Atributo.nombre.ilike("talla"), ValorAtributo.valor == talla)
#         )
        
#     if precio_min is not None: query = query.filter(Stock.precio_venta >= precio_min)
#     if precio_max is not None: query = query.filter(Stock.precio_venta <= precio_max)
#     if solo_vendidos: query = query.filter(Stock.cantidad == 0)

#     # Ordenamiento
#     if ordenar_por == "precio_asc": query = query.order_by(Stock.precio_venta.asc())
#     elif ordenar_por == "precio_desc": query = query.order_by(Stock.precio_venta.desc())
#     elif ordenar_por == "stock_asc": query = query.order_by(Stock.cantidad.asc())
#     elif ordenar_por == "stock_desc": query = query.order_by(Stock.cantidad.desc())
#     else: query = query.order_by(Stock.id.desc())

#     # 4. Conteo y Carga
#     total = query.distinct().count()

#     stocks_db = (
#         query.distinct()
#         .options(
#             selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.categoria),
#             selectinload(Stock.variante).selectinload(Variante.producto).selectinload(Producto.marca),
#             selectinload(Stock.variante).selectinload(Variante.imagenes),
#             selectinload(Stock.valores).selectinload(ValorAtributo.atributo)
#         )
#         .offset(offset)
#         .limit(limit)
#         .all()
#     )

#     # 5. APLANAMIENTO DE DATOS
#     resultados = []
#     for s in stocks_db:
#         v = s.variante
#         p = v.producto
        
#         talla_val = None
#         atributos_extra = {}
#         for val in s.valores:
#             if val.atributo:
#                 nombre_attr = val.atributo.nombre.lower()
#                 if nombre_attr in ['talla', 'size', 'medida']:
#                     talla_val = val.valor
#                 else:
#                     atributos_extra[nombre_attr] = val.valor

#         img_url = None
#         if v.imagenes:
#             img_sorted = sorted(v.imagenes, key=lambda x: x.orden or 0)
#             if img_sorted:
#                 img_url = img_sorted[0].url

#         resultados.append({
#             "stock_id": s.id,
#             "stock_sku": s.sku,
#             "variante_id": v.id,
#             "producto_id": p.id,
#             "producto_nombre": p.nombre,
#             "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
#             "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
#             "hex_identidad": v.hex_identidad,
#             "identidad_variante": v.identidad_variante,
#             "imagen_cover": img_url,
#             "etiqueta": s.etiqueta,
#             "talla": talla_val,
#             "atributos_extra": atributos_extra,
#             "stock_disponible": s.cantidad,
#             "precio_compra": float(s.precio_compra),
#             "precio_venta": float(s.precio_venta),
#             "descuento": float(s.descuento or 0),
#             "ubicacion_almacen": s.ubicacion, # ✨ AQUÍ ESTÁ EL CAMBIO (de 'v' a 's')
#             "canales": {
#                 "web": s.publicar_web,
#                 "vinted": s.publicar_vinted,
#                 "wallapop": s.publicar_wallapop
#             }
#         })

#     return {"total": total, "items": resultados}









































# # =====================================================
# # DETALLE COMPLETO (Para Edición)
# # =====================================================
# def obtener_producto_completo(db: Session, p_id: int):
#     producto = (
#         db.query(Producto)
#         .options(
#             joinedload(Producto.categoria),
#             joinedload(Producto.marca),
#             joinedload(Producto.variantes)
#                 .joinedload(Variante.stocks)
#                 .joinedload(Stock.valores)
#                 .joinedload(ValorAtributo.atributo),
#             joinedload(Producto.variantes).joinedload(Variante.imagenes)
#         )
#         .filter(Producto.id == p_id)
#         .first()
#     )

#     if not producto: return None

#     return {
#         "id": producto.id,
#         "nombre": producto.nombre,
#         "fecha_registro": producto.fecha_registro,
#         "fecha_actualizacion": producto.fecha_actualizacion,
#         "descripcion": producto.descripcion,
#         "tipo": producto.tipo,
#         "estado": producto.estado,
#         "publico_objetivo": producto.publico_objetivo,
#         "categoria_id": producto.categoria_id,
#         "marca": producto.marca,
        
#         # ✨ 1. ORDENAMOS LAS VARIANTES ANTES DE DIBUJARLAS
#         "variantes": [
#             {
#                 "id": v.id,
#                 "hex_identidad": v.hex_identidad,
#                 "identidad_variante": v.identidad_variante,
#                 "descripcion": v.descripcion,
#                 "orden": v.orden,
#                 "imagenes": [img.url for img in sorted(v.imagenes, key=lambda x: x.orden or 0)],
                
#                 # ✨ 2. ORDENAMOS LOS STOCKS ANTES DE DIBUJARLOS
#                 "stocks": [
#                     {
#                         "id": s.id,
#                         "sku": s.sku,
#                         "etiqueta": s.etiqueta,
#                         "ubicacion": s.ubicacion, 
#                         "cantidad": s.cantidad,
#                         "precio_compra": s.precio_compra,
#                         "precio_venta": s.precio_venta,
#                         "descuento": s.descuento,
#                         "proveedor_id": s.proveedor_id,
#                         "orden": s.orden,
#                         "proveedor": {"id": s.proveedor.id, "nombre_proveedor": s.proveedor.nombre_proveedor} if s.proveedor else None,
#                         "publicar_web": s.publicar_web,
#                         "publicar_vinted": s.publicar_vinted,
#                         "publicar_wallapop": s.publicar_wallapop,
#                         "fecha_compra": s.fecha_compra.isoformat() if s.fecha_compra else None,
#                         "atributos": [{"nombre": val.atributo.nombre, "valor": val.valor} for val in s.valores]
                        
#                     # ✨ AQUÍ ESTÁ EL TRUCO PARA ORDENAR LOS STOCKS
#                     } for s in sorted([st for st in v.stocks if st.activo], key=lambda x: x.orden or 0)
#                 ]
                
#             # ✨ AQUÍ ESTÁ EL TRUCO PARA ORDENAR LAS VARIANTES
#             } for v in sorted([var for var in producto.variantes if var.activo], key=lambda x: x.orden or 0)
#         ]
#     }




# # =====================================================
# # EDITAR PRODUCTO COMPLETO
# # =====================================================
# def editar_producto_completo(
#     db: Session, 
#     producto_id: int, 
#     nombre: str, 
#     descripcion: str, 
#     categoria_id: int, 
#     tipo: str, 
#     estado: str,
#     publico_objetivo: str, 
#     variantes: str, 
#     marca_id: Optional[int] = None, 
#     marca_nombre: Optional[str] = None, 
#     imagenes: Optional[Dict[str, List]] = None
# ):
#     # 1. Buscar el producto existente
#     producto = db.query(Producto).filter(Producto.id == producto_id).first()
#     if not producto:
#         return None

#     # 2. Actualizar campos básicos
#     producto.nombre = nombre
#     producto.descripcion = descripcion
#     producto.categoria_id = categoria_id
#     producto.tipo = tipo
#     producto.estado = estado
#     producto.publico_objetivo = publico_objetivo
    
#     # 3. Lógica de Marca
#     m_id = int(marca_id) if (marca_id and str(marca_id).isdigit() and int(marca_id) > 0) else None
#     if m_id:
#         producto.marca_id = m_id
#     elif marca_nombre and marca_nombre.strip():
#         nombre_clean = marca_nombre.strip()
#         marca_existente = db.query(Marca).filter(Marca.nombre.ilike(nombre_clean)).first()
#         if marca_existente:
#             producto.marca_id = marca_existente.id
#         else:
#             nueva_m = crear_marca(db, nombre=nombre_clean)
#             producto.marca_id = nueva_m.id

#     # 4. Procesar Variantes (JSON)
#     variantes_data = json.loads(variantes)
#     ids_variantes_vienen = [v.get("id") for v in variantes_data if v.get("id")]
    
#     # Desactivar variantes que ya no vienen en el JSON
#     for v_old in producto.variantes:
#         if v_old.id not in ids_variantes_vienen:
#             v_old.activo = False 

#     # --- BUCLE DE VARIANTES (Ordenadas por el Drag & Drop de variantes) ---
#     for indice_v, v_data in enumerate(variantes_data):
#         v_id = v_data.get("id")
#         v_temp_id = str(v_data.get("temp_id"))
        
#         if v_id:
#             nv = db.query(Variante).filter(Variante.id == v_id).first()
#             if nv:
#                 nv.hex_identidad = v_data.get("hex_identidad")
#                 nv.identidad_variante = v_data.get("identidad_variante")
#                 nv.ubicacion = v_data.get("ubicacion")
#                 nv.descripcion = v_data.get("descripcion")
#                 nv.orden = indice_v  # ✨ Orden de variante
#                 nv.activo = True
#         else:
#             nv = Variante(
#                 producto_id=producto.id,
#                 sku="TEMP",
#                 hex_identidad=v_data.get("hex_identidad"),
#                 identidad_variante=v_data.get("identidad_variante"),
#                 descripcion=v_data.get("descripcion"),
#                 orden=indice_v  # ✨ Orden para nueva variante
#             )
#             db.add(nv)
#             db.flush() 
#             nv.sku = generar_sku(tipo, nv.id)

#         # --- GESTIÓN DE IMÁGENES (Ordenadas por el Drag & Drop de imágenes) ---
#         lista_mezclada = v_data.get("imagenes", []) 
#         urls_permanecen = {item.strip() for item in lista_mezclada if isinstance(item, str) and item.startswith('http')}
        
#         imagenes_en_db = db.query(Imagen).filter(Imagen.variante_id == nv.id).all()
#         for img_db in imagenes_en_db:
#             if img_db.url.strip() not in urls_permanecen:
#                 try:
#                     delete_image_from_s3(img_db.url)
#                 except: pass
#                 db.delete(img_db)

#         for indice_img, item in enumerate(lista_mezclada):
#             item_clean = item.strip() if isinstance(item, str) else item
            
#             if isinstance(item_clean, str) and item_clean.startswith('http'):
#                 img_existente = db.query(Imagen).filter(Imagen.url == item_clean, Imagen.variante_id == nv.id).first()
#                 if img_existente:
#                     img_existente.orden = indice_img # ✨ Sincronizamos orden de imagen
            
#             elif isinstance(item_clean, str) and item_clean.startswith('NUEVA_'):
#                 key_archivo = f"file_{v_temp_id}_{item_clean}"
#                 if imagenes and key_archivo in imagenes:
#                     file_to_upload = imagenes[key_archivo][0]
#                     url_s3 = upload_image_to_s3(file_to_upload, folder=f"productos/{producto.id}/{nv.id}")
#                     db.add(Imagen(url=url_s3, variante_id=nv.id, orden=indice_img)) # ✨ Orden nueva imagen

#         # --- GESTIÓN DE STOCKS (Ordenados por el Drag & Drop de stocks) ---
#         stocks_data = v_data.get("stocks", [])
#         ids_stocks_vienen = [s.get("id") for s in stocks_data if s.get("id")]
        
#         db.query(Stock).filter(
#             Stock.variante_id == nv.id, 
#             Stock.id.notin_(ids_stocks_vienen) if ids_stocks_vienen else Stock.id > 0
#         ).update({"activo": False}, synchronize_session=False)

#         for indice_s, s_data in enumerate(stocks_data):
#             s_id = s_data.get("id")
            
#             # Limpieza del proveedor_id
#             raw_p_id = s_data.get("proveedor_id")
#             p_id = int(raw_p_id) if (raw_p_id and str(raw_p_id).isdigit() and int(raw_p_id) > 0) else None

#             if not p_id:
#                 nombre_p = s_data.get("proveedor_nombre_nuevo") or s_data.get("proveedor")
#                 if nombre_p and nombre_p.strip():
#                     prov_obj = buscar_o_crear(db, nombre_p.strip())
#                     p_id = prov_obj.id if prov_obj else None

#             fecha_c = s_data.get("fecha_compra")
#             if not fecha_c or fecha_c == "": fecha_c = None

#             if s_id:
#                 so = db.query(Stock).filter(Stock.id == s_id).first()
#                 if so:
#                     so.etiqueta = s_data.get("etiqueta")
#                     so.ubicacion = s_data.get("ubicacion")
#                     so.cantidad = s_data.get("cantidad", 0) or s_data.get("stock", 0)
#                     so.precio_compra = s_data.get("precio_compra", 0)
#                     so.precio_venta = s_data.get("precio_venta", 0)
#                     so.proveedor_id = p_id 
#                     so.fecha_compra = fecha_c
#                     so.descuento = s_data.get("descuento", 0)
#                     so.publicar_web = s_data.get("publicar_web", False)
#                     so.orden = indice_s # ✨ GUARDAMOS EL ORDEN DEL STOCK
#                     so.activo = True
#             else:
#                 so = Stock(
#                     variante_id=nv.id, 
#                     proveedor_id=p_id,
#                     etiqueta=s_data.get("etiqueta", "Única"),
#                     ubicacion=s_data.get("ubicacion", ""),
#                     cantidad=s_data.get("cantidad", 0) or s_data.get("stock", 0),
#                     precio_compra=s_data.get("precio_compra", 0),
#                     precio_venta=s_data.get("precio_venta", 0),
#                     fecha_compra=fecha_c,
#                     descuento=s_data.get("descuento", 0),
#                     publicar_web=s_data.get("publicar_web", False),
#                     orden=indice_s, # ✨ Orden para nuevo stock
#                     sku="TEMP"
#                 )
#                 db.add(so)
#                 db.flush()
#                 so.sku = generar_sku(tipo, so.id)

#             if s_data.get("atributos"):
#                 guardar_valores_stock(db, so, s_data.get("atributos"))

#     db.commit()
#     db.refresh(producto)
#     return producto






# #from sqlalchemy.orm import Session
# # Asegúrate de importar tus modelos correctamente:

# # Importa tu función de S3
# # from app.utils.s3_utils import delete_image_from_s3 

# # =====================================================
# # GESTIÓN DE PAPELERA Y ELIMINACIÓN
# # =====================================================




# def vaciar_producto_papelera(db: Session, p_id: int):
#     """
#     2. HARD DELETE (Destrucción permanente)
#     Solo se ejecuta si el producto NO tiene historial de ventas.
#     Limpia el almacenamiento en AWS S3 y borra los registros en cascada.
#     """
#     producto = db.query(Producto).filter(Producto.id == p_id).first()
#     if not producto:
#         return {"success": False, "mensaje": "El producto no existe."}
    
#     # Verificamos si tiene ventas reales
#     tiene_ventas = db.query(DetalleVenta).join(
#         Stock, DetalleVenta.stock_id == Stock.id
#     ).join(
#         Variante, Stock.variante_id == Variante.id
#     ).filter(
#         Variante.producto_id == p_id
#     ).first() is not None

#     # Si tiene ventas, bloqueamos la destrucción para proteger la contabilidad
#     if tiene_ventas:
#         return {
#             "success": False, 
#             "mensaje": "⚠️ No puedes destruir este producto porque tiene ventas registradas. Mantenlo en la papelera."
#         }
    
#     # Si no tiene ventas, ¡Destrucción total (Física + S3)!
#     print(f"🧹 Iniciando borrado permanente del producto {p_id}...")
#     for variante in producto.variantes:
#         for img in getattr(variante, 'imagenes', []):
#             try: 
#                 # Borramos la foto física del bucket de Amazon S3
#                 delete_image_from_s3(img.url) 
#                 print(f"✅ S3: Imagen borrada -> {img.url}")
#             except Exception as e: 
#                 print(f"⚠️ Error S3: {e}")
    
#     # Borrado en cascada de la BD (Producto -> Variantes -> Stocks -> Imagenes)
#     db.delete(producto)
#     db.commit()
    
#     return {"success": True, "mensaje": "✅ Producto eliminado permanentemente."}



# def obtener_productos_papelera(db: Session, page: int = 1, limit: int = 10):
#     offset = (page - 1) * limit
    
#     # ✨ CORRECCIÓN: Filtramos por activo == False (Papelera)
#     query = (
#         db.query(Producto)
#         .filter(Producto.activo == False)
#         .options(
#             joinedload(Producto.categoria),
#             joinedload(Producto.marca),
#             joinedload(Producto.variantes).joinedload(Variante.stocks),
#             joinedload(Producto.variantes).joinedload(Variante.imagenes)
#         )
#         .order_by(Producto.id.desc())
#     )

#     total = query.count()
#     productos = query.offset(offset).limit(limit).all()

#     resultados = []
#     for p in productos:
#         stock_acumulado = sum(s.cantidad for v in p.variantes for s in v.stocks)
#         precios = [s.precio_venta for v in p.variantes for s in v.stocks]
        
#         imagen_cover = None
#         if p.variantes:
#             # Quitamos el filtro de activo para que muestre la foto en la papelera
#             variante_principal = next((v for v in p.variantes if v.imagenes), None)
#             if variante_principal:
#                 imagenes_ordenadas = sorted(variante_principal.imagenes, key=lambda img: img.orden or 0)
#                 if imagenes_ordenadas:
#                     imagen_cover = imagenes_ordenadas[0].url

#         colores_unicos = list({v.hex_identidad for v in p.variantes if v.hex_identidad})
        
#         resultados.append({
#             "id": p.id,
#             "nombre": p.nombre,
#             "sku": p.sku,
#             "tipo": p.tipo,
#             "categoria": {"id": p.categoria.id, "nombre": p.categoria.nombre} if p.categoria else None,
#             "marca": {"id": p.marca.id, "nombre": p.marca.nombre} if p.marca else None,
#             "imagen": imagen_cover,
#             "stock_total": stock_acumulado,
#             "precio_min": min(precios) if precios else None,
#             "precio_max": max(precios) if precios else None,
#             "colores": colores_unicos,
#             "canales": {
#                 "web": False, 
#                 "vinted": False,
#                 "wallapop": False
#             }
#         })

#     return {"total": total, "items": resultados}


# def mover_a_papelera(db: Session, p_id: int):
#     """
#     EL PARAGUAS SE CIERRA:
#     Solo apagamos el producto. Automáticamente sus variantes/stocks 
#     dejarán de ser accesibles desde la tienda.
#     """
#     producto = db.query(Producto).filter(Producto.id == p_id).first()
#     if not producto: return False
    
#     # Apagamos solo al padre
#     producto.activo = False 
    
#     db.commit()
#     return {"success": True, "mensaje": "🗑️ Producto movido a la papelera."}


# def restaurar_de_papelera(db: Session, p_id: int):
#     """
#     EL PARAGUAS SE ABRE:
#     Encendemos el producto. Las variantes que habías borrado individualmente 
#     en el pasado seguirán borradas, y las sanas volverán a verse.
#     """
#     producto = db.query(Producto).filter(Producto.id == p_id).first()
#     if not producto: return False
    
#     # Encendemos solo al padre
#     producto.activo = True
    
#     db.commit()
#     return {"success": True, "mensaje": "♻️ Producto restaurado con éxito."}






























