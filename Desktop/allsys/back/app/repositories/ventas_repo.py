from datetime import datetime
import random
import string
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import desc, or_, cast, String, func
from fastapi import HTTPException

# Modelos y Schemas
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
def registrar_venta(db: Session, data: VentaCreate):
    try:
        # 1. Calcular Totales
        subtotal = sum(d.cantidad * d.precio_unitario for d in data.detalles)
        total_final = (subtotal + data.costo_envio) - data.descuento_total

        # ✨ 2. DELEGAR AL SERVICIO DE CLIENTES (Adiós a la función Dios)
        # Le pasamos toda la data y él nos devuelve el ID del cliente o None
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
            
            cliente_id=cliente_id, 
            nombre_cliente=data.nombre_cliente, # Guardamos cómo se llamó en ESTE pedido
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
def obtener_venta_por_id(db: Session, venta_id: int):
    venta = db.query(Venta).options(
        joinedload(Venta.detalles)
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

    # 1. Actualizar campos
    for key, value in datos.items():
        if hasattr(venta, key) and value is not None:
            if key in ["total", "subtotal", "costo_envio", "descuento_total"]:
                setattr(venta, key, float(value))
            else:
                setattr(venta, key, value)

    # 2. Recalcular si modifican el total
    if "total" in datos:
        venta.subtotal = float(datos["total"]) - (venta.costo_envio or 0) + (venta.descuento_total or 0)

    # 3. Lógica de devolución/resta de stock según estado
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
    db: Session, page: int = 1, limit: int = 10, search: str = None,
    estado_venta: str = None, canal: str = None, fecha_inicio: str = None,
    fecha_fin: str = None, vendedor: str = None, comprador: str = None
):
    offset = (page - 1) * limit
    query = db.query(Venta)

    # Filtros
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Venta.codigo_venta.ilike(term),
                Venta.nombre_cliente.ilike(term),
                Venta.email_cliente.ilike(term),
                cast(Venta.id, String).ilike(term)
            )
        )
    if estado_venta: query = query.filter(Venta.estado_venta == estado_venta)
    if canal: query = query.filter(Venta.canal == canal)
    if vendedor: query = query.filter(Venta.vendedor == vendedor)
    if comprador: query = query.filter(Venta.nombre_cliente.ilike(f"%{comprador}%"))
    if fecha_inicio: query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin: query = query.filter(Venta.fecha <= f"{fecha_fin} 23:59:59")

    # Cálculos globales
    total_recaudado = query.with_entities(func.sum(Venta.total)).scalar() or 0
    total_costo = (
        db.query(func.sum(DetalleVenta.cantidad * Stock.precio_compra))
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .join(Stock, DetalleVenta.stock_id == Stock.id)
        .filter(Venta.id.in_(query.with_entities(Venta.id)))
        .scalar() or 0
    )
    total_beneficio = float(total_recaudado) - float(total_costo)

    # Paginación
    total_count = query.count()
    ventas_db = (
        query.options(
            selectinload(Venta.detalles)
            .selectinload(DetalleVenta.stock)
            .selectinload(Stock.variante)
            .selectinload(Variante.imagenes)
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
                if imgs:
                    imagen_cover = imgs[0].url

        if len(nombres_productos) > 1:
            resumen = f"{nombres_productos[0]} y {len(nombres_productos) - 1} más"
        elif len(nombres_productos) == 1:
            resumen = nombres_productos[0]
        else:
            resumen = "Sin productos"

        resultados.append({
            "id": venta.id,
            "codigo_venta": venta.codigo_venta,
            "fecha": venta.fecha.isoformat() if venta.fecha else None,
            "nombre_cliente": venta.nombre_cliente,
            "canal": venta.canal,
            "vendedor": venta.vendedor,
            "metodo_pago": venta.metodo_pago,
            "estado_venta": venta.estado_venta,
            "total": float(venta.total),
            "imagen_cover": imagen_cover,
            "resumen_productos": resumen
        })

    return {
        "total": total_count,
        "items": resultados,
        "suma_recaudado": float(total_recaudado),
        "suma_beneficio": float(total_beneficio)
    }