from datetime import datetime
import random
import string
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import desc, or_, cast, String, func
from fastapi import HTTPException
from app.models.categorias_model import Categoria
# Modelos y Schemas
from app.models.clientes_model import Cliente
from app.models.producto_model import Producto
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from app.models.variantes_model import Variante
from app.schemas.ventas_schema import VentaCreate

# ✨ IMPORTAMOS NUESTRO NUEVO SERVICIO ESTRELLA
from app.services.cliente_services import procesar_cliente_omnicanal


# =====================================================
# GENERADOR DE CÓDIGOS ANTICOLISIONES 🛡️
# =====================================================
def generar_codigo_venta(db: Session) -> str:
    """
    Genera un código tipo VEN-260406-A1B2 (VEN-AÑOMESDIA-RANDOM)
    y verifica en la BD que sea 100% único antes de devolverlo.
    """
    while True:
        fecha_str = datetime.utcnow().strftime("%y%m%d")
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        codigo_candidato = f"VEN-{fecha_str}-{rand}"
        
        existe = db.query(Venta).filter(Venta.codigo_venta == codigo_candidato).first()
        if not existe:
            return codigo_candidato


# =====================================================
# REGISTRO DE VENTA 💰
# =====================================================
# =====================================================
# REGISTRO DE VENTA 💰
# =====================================================
def registrar_venta(db: Session, data: VentaCreate):
    try:
        # 1. Calcular Totales
        subtotal = sum(d.cantidad * d.precio_unitario for d in data.detalles)
        total_final = (subtotal + data.costo_envio) - data.descuento_total

        # ✨ BLOQUEO ESTRICTO DE NOMBRE: Capturamos lo que escribió el usuario.
        # Si está vacío, forzamos a que sea None. Así evitamos que la lógica del CRM 
        # copie el @usuario o el teléfono aquí por accidente.
        nombre_real_estricto = data.nombre_cliente.strip() if data.nombre_cliente and data.nombre_cliente.strip() else None

        # 2. DELEGAR AL SERVICIO DE CLIENTES
        cliente_id = procesar_cliente_omnicanal(db=db, data=data)

        # 3. CREACIÓN DE LA VENTA PADRE
        nueva_venta = Venta(
            codigo_venta=generar_codigo_venta(db),
            fecha=data.fecha or datetime.utcnow(),
            canal=data.canal,
            vendedor=data.vendedor,
            metodo_pago=data.metodo_pago,
            estado_venta=data.estado_venta,
            estado_pago=data.estado_pago,
            pais=data.pais,
            cliente_id=cliente_id, 
            nombre_cliente=nombre_real_estricto, # 👈 AQUÍ USAMOS LA VARIABLE PROTEGIDA
            email_cliente=data.email_cliente,
            
            subtotal=subtotal,
            costo_envio=data.costo_envio,
            descuento_total=data.descuento_total,
            total=total_final,
            transaccion_id_externo=data.transaccion_id_externo,
            empresa_transporte=data.empresa_transporte,
            numero_seguimiento=data.numero_seguimiento
        )
        
        db.add(nueva_venta)
        db.flush() 
        
        # ... (El resto del código de gestión de stock queda exactamente igual) ...

        # 4. GESTIÓN DE STOCK (Detalles de la venta)
        for item in data.detalles:
            stock_db = db.query(Stock).filter(Stock.id == item.stock_id).first()
            if not stock_db:
                raise HTTPException(status_code=404, detail=f"Stock ID {item.stock_id} no encontrado.")

            if stock_db.cantidad < item.cantidad:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {stock_db.variante.producto.nombre}. Disponible: {stock_db.cantidad}")

            # Descontamos el stock
            stock_db.cantidad -= item.cantidad

            # Creamos el snapshot para la factura
            nuevo_detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                stock_id=stock_db.id,
                cantidad=item.cantidad,
                precio_unitario_en_venta=item.precio_unitario,
                nombre_producto_snapshot=stock_db.variante.producto.nombre,
                talla_snapshot=stock_db.etiqueta,
                color_snapshot=stock_db.variante.identidad_variante
            )
            db.add(nuevo_detalle)

        # 5. GUARDADO FINAL
        db.commit()
        db.refresh(nueva_venta)
        return nueva_venta

    except Exception as e:
        db.rollback() 
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error al procesar la venta: {str(e)}")


# =====================================================
# OBTENER UNA VENTA DETALLADA 📄
# =====================================================
# =====================================================
# OBTENER UNA VENTA DETALLADA 📄
# =====================================================
def obtener_venta_por_id(db: Session, venta_id: int):
    venta = db.query(Venta).options(
        joinedload(Venta.detalles),
        joinedload(Venta.cliente) # ✨ CLAVE: Cargamos el perfil del CRM
    ).filter(Venta.id == venta_id).first()
    return venta


# =====================================================
# ACTUALIZAR ESTADOS DE UNA VENTA 🔄
# =====================================================
def actualizar_venta(db: Session, venta_id: int, datos: dict):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")

    estado_anterior = venta.estado_venta
    estado_pago_anterior = venta.estado_pago
    estado_envio_anterior = venta.estado_envio

    # 1. Actualizar campos simples
    for key, value in datos.items():
        if hasattr(venta, key) and value is not None:
            if key in ["total", "subtotal", "costo_envio", "descuento_total"]:
                setattr(venta, key, float(value))
            else:
                setattr(venta, key, value)

    # 2. Recalcular si modifican el total
    if "total" in datos:
        venta.subtotal = float(datos["total"]) - (venta.costo_envio or 0) + (venta.descuento_total or 0)

    # ✨ 3. LÓGICA DE FECHAS AUTOMÁTICAS
    # Si pasa a Pagado y no tiene fecha_pago, pon la fecha actual
    if venta.estado_pago == "pagado" and estado_pago_anterior != "pagado":
        if not venta.fecha_pago:
            venta.fecha_pago = datetime.utcnow()
            
    # Si pasa a Enviado o Entregado y no tiene fecha_envio, pon la fecha actual
    if venta.estado_envio in ["enviado", "entregado"] and estado_envio_anterior not in ["enviado", "entregado"]:
        if not venta.fecha_envio:
            venta.fecha_envio = datetime.utcnow()

    # 4. Lógica de devolución/resta de stock según estado
    nuevo_estado = datos.get("estado_venta")
    if nuevo_estado and nuevo_estado != estado_anterior:
        
        # Devolver stock
        if nuevo_estado in ["cancelada", "devuelta"] and estado_anterior not in ["cancelada", "devuelta"]:
            for detalle in venta.detalles:
                if detalle.stock_id:
                    stock_db = db.query(Stock).filter(Stock.id == detalle.stock_id).first()
                    if stock_db:
                        stock_db.cantidad += detalle.cantidad
                        print(f"♻️ Stock devuelto: +{detalle.cantidad} uds al stock_id {stock_db.id}")

        # Reactivar stock
        elif nuevo_estado in ["procesando", "completada"] and estado_anterior in ["cancelada", "devuelta"]:
            for detalle in venta.detalles:
                if detalle.stock_id:
                    stock_db = db.query(Stock).filter(Stock.id == detalle.stock_id).first()
                    if stock_db:
                        if stock_db.cantidad < detalle.cantidad:
                            db.rollback()
                            raise HTTPException(
                                status_code=400, 
                                detail=f"No hay stock suficiente para reactivar esta venta. (ID Stock: {stock_db.id})"
                            )
                        stock_db.cantidad -= detalle.cantidad 
                        print(f"📉 Stock restado por reactivación: -{detalle.cantidad} uds al stock_id {stock_db.id}")

    try:
        db.commit()
        db.refresh(venta)
        return venta
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la venta: {str(e)}")


# =====================================================
# LISTAR VENTAS CON PAGINACIÓN Y FILTROS 📊
# =====================================================
def obtener_ventas_paginadas(
    db: Session, page: int = 1, limit: int = 10, 
    search_producto: str = None, tipo_busqueda_prod: str = "sku",
    search_codigo: str = None, 
    search_cliente: str = None, tipo_busqueda_cliente: str = "nombre", 
    estado_venta: str = None, canal: str = None, fecha_inicio: str = None,
    fecha_fin: str = None, vendedor: str = None, 
    marca_id: int = None, categoria_id: int = None
):
    offset = (page - 1) * limit
    query = db.query(Venta)

    # =====================================================
    # 1. FILTROS DE INVENTARIO (MAGIA DE JOINS Y RECURSIVIDAD)
    # =====================================================
    if marca_id or categoria_id:
        query = query.join(DetalleVenta, Venta.id == DetalleVenta.venta_id)\
                     .join(Stock, DetalleVenta.stock_id == Stock.id)\
                     .join(Variante, Stock.variante_id == Variante.id)\
                     .join(Producto, Variante.producto_id == Producto.id)

        if marca_id: query = query.filter(Producto.marca_id == marca_id)
            
        if categoria_id:
            todas_categorias = db.query(Categoria.id, Categoria.parent_id).all()
            ids_a_buscar = set([categoria_id])
            ids_para_procesar = set([categoria_id])
            
            while ids_para_procesar:
                hijos = set([c.id for c in todas_categorias if c.parent_id in ids_para_procesar and c.id not in ids_a_buscar])
                ids_a_buscar.update(hijos)
                ids_para_procesar = hijos
                
            query = query.filter(Producto.categoria_id.in_(list(ids_a_buscar)))
            
        query = query.distinct()

    # =====================================================
    # 2. CAJA 1: BÚSQUEDA POR PRODUCTO (SKU o ID)
    # =====================================================
    if search_producto and search_producto.strip():
        term_str = search_producto.strip()
        
        if tipo_busqueda_prod == "sku":
            term = f"%{term_str}%"
            query = query.filter(Venta.detalles.any(DetalleVenta.stock.has(Stock.sku.ilike(term))))
            
        elif tipo_busqueda_prod == "id_producto":
            if term_str.isdigit():
                query = query.filter(Venta.detalles.any(DetalleVenta.stock_id == int(term_str)))
            else:
                query = query.filter(False) # Forzar vacío si escriben letras en ID

    # =====================================================
    # 3. CAJA 2: BÚSQUEDA POR CÓDIGO DE VENTA (VEN-...)
    # =====================================================
    if search_codigo and search_codigo.strip():
        term_codigo = f"%{search_codigo.strip()}%"
        query = query.filter(Venta.codigo_venta.ilike(term_codigo))

    # =====================================================
    # 4. CAJA 3: BÚSQUEDA POR CLIENTE (Con Selector) 
    # =====================================================
    if search_cliente and search_cliente.strip():
        term_cliente = f"%{search_cliente.strip()}%"

        if tipo_busqueda_cliente == "nombre":
            query = query.filter(
                or_(
                    Venta.nombre_cliente.ilike(term_cliente),
                    Venta.cliente.has(Cliente.nombre.ilike(term_cliente)),
                    Venta.cliente.has(Cliente.apellidos.ilike(term_cliente)),
                    Venta.cliente.has(Cliente.usuario_vinted.ilike(term_cliente)),
                    Venta.cliente.has(Cliente.usuario_wallapop.ilike(term_cliente))
                )
            )
            
        elif tipo_busqueda_cliente == "email":
            query = query.filter(
                or_(
                    Venta.email_cliente.ilike(term_cliente),
                    Venta.cliente.has(Cliente.email.ilike(term_cliente))
                )
            )
            
        elif tipo_busqueda_cliente == "telefono":
            query = query.filter(Venta.cliente.has(Cliente.telefono.ilike(term_cliente)))
            
        elif tipo_busqueda_cliente == "documento":
            query = query.filter(Venta.cliente.has(Cliente.dni_nie.ilike(term_cliente)))

    # =====================================================
    # 5. FILTROS BÁSICOS Y FECHAS
    # =====================================================
    if estado_venta: query = query.filter(Venta.estado_venta == estado_venta)
    if canal: query = query.filter(Venta.canal == canal)
    if vendedor: query = query.filter(Venta.vendedor == vendedor)
    if fecha_inicio: query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin: query = query.filter(Venta.fecha <= f"{fecha_fin} 23:59:59")

    # =====================================================
    # 6. CÁLCULOS FINANCIEROS
    # =====================================================
    total_recaudado = query.with_entities(func.sum(Venta.total)).scalar() or 0
    total_costo = (
        db.query(func.sum(DetalleVenta.cantidad * Stock.precio_compra))
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .join(Stock, DetalleVenta.stock_id == Stock.id)
        .filter(Venta.id.in_(query.with_entities(Venta.id)))
        .scalar() or 0
    )
    total_beneficio = float(total_recaudado) - float(total_costo)

    # =====================================================
    # 7. EJECUCIÓN CON PAGINACIÓN
    # =====================================================
    total_count = query.count()
    ventas_db = (
        query.options(
            selectinload(Venta.detalles).selectinload(DetalleVenta.stock).selectinload(Stock.variante).selectinload(Variante.imagenes),
            selectinload(Venta.cliente) # ✨ AÑADIDO: Carga los datos del CRM de forma optimizada
        )
        .order_by(desc(Venta.fecha))
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Aplanado para Angular
    resultados = []
    for venta in ventas_db:
        imagen_cover = None
        nombres_productos = []
        for detalle in venta.detalles:
            nombres_productos.append(detalle.nombre_producto_snapshot)
            if not imagen_cover and detalle.stock and detalle.stock.variante and detalle.stock.variante.imagenes:
                imgs = sorted(detalle.stock.variante.imagenes, key=lambda x: x.orden or 0)
                if imgs: imagen_cover = imgs[0].url

        resumen = f"{nombres_productos[0]} y {len(nombres_productos) - 1} más" if len(nombres_productos) > 1 else (nombres_productos[0] if len(nombres_productos) == 1 else "Sin productos")

        # ✨ NUEVA LÓGICA: Extraer el mejor identificador posible del CRM
        identificador_crm = "Anónimo"
        if venta.cliente:
            if venta.canal == "vinted" and venta.cliente.usuario_vinted:
                identificador_crm = f"@{venta.cliente.usuario_vinted}" # 👈 Saca @usuario
            elif venta.canal == "wallapop" and venta.cliente.usuario_wallapop:
                identificador_crm = f"@{venta.cliente.usuario_wallapop}" # 👈 Saca @usuario
            elif venta.cliente.telefono:
                identificador_crm = venta.cliente.telefono # 👈 Saca Teléfono
            elif venta.cliente.email:
                identificador_crm = venta.cliente.email # 👈 Saca Email
            elif venta.cliente.dni_nie:
                identificador_crm = venta.cliente.dni_nie
        elif venta.email_cliente:
            identificador_crm = venta.email_cliente

        resultados.append({
            "id": venta.id, 
            "codigo_venta": venta.codigo_venta,
            "fecha": venta.fecha.isoformat() if venta.fecha else None,
            
            # Mandamos ambos datos: El nombre real (si lo hay) y el identificador
            "nombre_cliente": venta.nombre_cliente, 
            "identificador_cliente": identificador_crm, # ✨ NUEVO CAMPO ENVIADO AL FRONT
            
            "canal": venta.canal,
            "vendedor": venta.vendedor, 
            "metodo_pago": venta.metodo_pago,
            "estado_venta": venta.estado_venta, 
            "total": float(venta.total),
            "imagen_cover": imagen_cover, 
            "resumen_productos": resumen,
            "pais": venta.pais,
        })

    return {
        "total": total_count, "items": resultados,
        "suma_recaudado": float(total_recaudado), "suma_beneficio": float(total_beneficio)
    }
























def contar_compras_cliente(db: Session, identificador: str):
    identificador = identificador.strip()
    
    # Buscamos al cliente ignorando mayúsculas/minúsculas
    cliente = db.query(Cliente).filter(
        or_(
            Cliente.email.ilike(identificador),
            Cliente.telefono.ilike(identificador),
            Cliente.usuario_vinted.ilike(identificador.replace("@", "")), # Quitamos el @ por si acaso
            Cliente.usuario_wallapop.ilike(identificador.replace("@", "")),
            Cliente.dni_nie.ilike(identificador)
        )
    ).first()

    if not cliente:
        print(f"🔍 CRM: No se encontró ficha para {identificador}")
        return 0
    
    # Contamos ventas
    total = db.query(func.count(Venta.id)).filter(Venta.cliente_id == cliente.id).scalar()
    print(f"📈 CRM: {identificador} tiene {total} ventas.")
    return total








# def desactivar_cliente(db: Session, cliente_id: int):
#     cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
#     if not cliente:
#         raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
#     # Simplemente lo marcamos como inactivo
#     cliente.activo = False
#     db.commit()
#     return {"message": "Cliente desactivado. Sus datos se mantienen por historial pero no aparecerá en búsquedas activas."}