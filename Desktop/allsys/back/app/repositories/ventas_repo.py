from datetime import datetime
import random
import string
from sqlalchemy.orm import Session
from app.models.variantes_model import Variante
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from fastapi import HTTPException

from app.schemas.ventas_schema import VentaCreate



# =====================================================
# GENERADOR DE CÓDIGOS ANTICOLISIONES 🛡️
# =====================================================
def generar_codigo_venta(db: Session) -> str:
    """
    Genera un código tipo VEN-260406-A1B2 (VEN-AÑOMESDIA-RANDOM)
    y verifica en la BD que sea 100% único antes de devolverlo.
    """
    while True:
        # 1. Obtenemos la fecha en formato corto (Ej: 260406 para 6 de Abril de 2026)
        fecha_str = datetime.utcnow().strftime("%y%m%d")
        
        # 2. Generamos 4 caracteres aleatorios
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # 3. Armamos el código final
        codigo_candidato = f"VEN-{fecha_str}-{rand}"
        
        # 4. Preguntamos a la base de datos si ya existe
        existe = db.query(Venta).filter(Venta.codigo_venta == codigo_candidato).first()
        
        # Si no existe, rompemos el bucle y devolvemos este código seguro
        if not existe:
            return codigo_candidato
        


def registrar_venta(db: Session, data: VentaCreate):
    try:
        # 1. Calcular Totales
        subtotal = sum(d.cantidad * d.precio_unitario for d in data.detalles)
        total_final = (subtotal + data.costo_envio) - data.descuento_total

        # 2. Crear el objeto Venta (Padre)
        nueva_venta = Venta(
            codigo_venta=generar_codigo_venta(db),
            fecha=data.fecha or datetime.utcnow(),
            canal=data.canal,
            vendedor=data.vendedor,
            metodo_pago=data.metodo_pago,
            nombre_cliente=data.nombre_cliente,
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
        db.flush() # Para obtener el ID de la venta sin hacer commit aún

        # 3. Procesar cada producto del carrito
        for item in data.detalles:
            # Buscamos el stock y cargamos producto/variante para el snapshot
            stock_db = db.query(Stock).filter(Stock.id == item.stock_id).first()
            
            if not stock_db:
                raise HTTPException(status_code=404, detail=f"Stock ID {item.stock_id} no encontrado.")

            # 🛡️ VALIDACIÓN CRÍTICA: ¿Hay suficiente stock?
            if stock_db.cantidad < item.cantidad:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock insuficiente para {stock_db.variante.producto.nombre}. Disponible: {stock_db.cantidad}"
                )

            # 📉 RESTAR STOCK
            stock_db.cantidad -= item.cantidad

            # 📸 CREAR SNAPSHOT (Foto histórica)
            nombre_prod = stock_db.variante.producto.nombre
            color_prod = stock_db.variante.identidad_variante
            talla_prod = stock_db.etiqueta

            nuevo_detalle = DetalleVenta(
                venta_id=nueva_venta.id,
                stock_id=stock_db.id,
                cantidad=item.cantidad,
                precio_unitario_en_venta=item.precio_unitario,
                nombre_producto_snapshot=nombre_prod,
                talla_snapshot=talla_prod,
                color_snapshot=color_prod
            )
            db.add(nuevo_detalle)

        # 4. Finalizar Transacción
        db.commit()
        db.refresh(nueva_venta)
        return nueva_venta

    except Exception as e:
        db.rollback() # Si algo falla, deshacemos todo (incluso la resta de stock)
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Error al procesar la venta: {str(e)}")
    














from sqlalchemy.orm import joinedload

def obtener_venta_por_id(db: Session, venta_id: int):
    venta = db.query(Venta).options(
        joinedload(Venta.detalles)
    ).filter(Venta.id == venta_id).first()
    return venta

def actualizar_venta(db: Session, venta_id: int, datos: dict):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada.")

    estado_anterior = venta.estado_venta

    # Actualizamos todos los campos enviados
    for key, value in datos.items():
        if hasattr(venta, key) and value is not None:
            setattr(venta, key, value)

    # 🛡️ LÓGICA DE DEVOLUCIÓN DE STOCK (ANTI-PÉRDIDAS)
    nuevo_estado = datos.get("estado_venta")
    
    # Si la venta se cancela o se devuelve, devolvemos el stock al inventario
    if nuevo_estado in ["cancelada", "devuelta"] and estado_anterior not in ["cancelada", "devuelta"]:
        for detalle in venta.detalles:
            if detalle.stock_id:
                stock_db = db.query(Stock).filter(Stock.id == detalle.stock_id).first()
                if stock_db:
                    stock_db.cantidad += detalle.cantidad
                    print(f"♻️ Stock devuelto: +{detalle.cantidad} uds al stock_id {stock_db.id}")

    # Si se habían cancelado y ahora se vuelven a activar (raro, pero posible)
    elif nuevo_estado in ["procesando", "completada"] and estado_anterior in ["cancelada", "devuelta"]:
        for detalle in venta.detalles:
            if detalle.stock_id:
                stock_db = db.query(Stock).filter(Stock.id == detalle.stock_id).first()
                if stock_db:
                    stock_db.cantidad -= detalle.cantidad # Volvemos a restar el stock
                    if stock_db.cantidad < 0:
                        db.rollback()
                        raise HTTPException(status_code=400, detail="No hay stock suficiente para reactivar esta venta.")

    db.commit()
    db.refresh(venta)
    return venta





















from sqlalchemy import desc, or_, cast, String
from sqlalchemy.orm import selectinload

from sqlalchemy import desc, or_, cast, String, func
from sqlalchemy.orm import Session, selectinload
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from app.models.variantes_model import Variante

def obtener_ventas_paginadas(
    db: Session,
    page: int = 1,
    limit: int = 10,
    search: str = None,
    estado_venta: str = None,
    canal: str = None,
    fecha_inicio: str = None,
    fecha_fin: str = None,
    vendedor: str = None,
    comprador: str = None
):
    offset = (page - 1) * limit
    
    # 1. Iniciamos la consulta base
    query = db.query(Venta)

    # --- APLICACIÓN DE FILTROS ---
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
    
    if estado_venta: 
        query = query.filter(Venta.estado_venta == estado_venta)
    
    if canal: 
        query = query.filter(Venta.canal == canal)
    
    if vendedor: 
        query = query.filter(Venta.vendedor == vendedor)
    
    if comprador: 
        query = query.filter(Venta.nombre_cliente.ilike(f"%{comprador}%"))
    
    if fecha_inicio: 
        query = query.filter(Venta.fecha >= fecha_inicio)
    
    if fecha_fin: 
        query = query.filter(Venta.fecha <= f"{fecha_fin} 23:59:59")

    # 2. CÁLCULO DE TOTALES FILTRADOS (Antes de paginar)
    # Total Recaudado: Suma de la columna 'total' de todas las ventas filtradas
    total_recaudado = query.with_entities(func.sum(Venta.total)).scalar() or 0

    # Total Beneficio: Suma de (Total Venta - Costo de productos)
    # Unimos con DetalleVenta y Stock para obtener el precio_compra de cada artículo
    total_costo = (
        db.query(func.sum(DetalleVenta.cantidad * Stock.precio_compra))
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .join(Stock, DetalleVenta.stock_id == Stock.id)
        # IMPORTANTE: Aplicamos los mismos filtros de la query original
        .filter(Venta.id.in_(query.with_entities(Venta.id)))
        .scalar() or 0
    )
    
    total_beneficio = float(total_recaudado) - float(total_costo)

    # 3. PAGINACIÓN Y CARGA DE DATOS (Eager Loading)
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

    # 4. APLANADO DE DATOS PARA ANGULAR
    resultados = []
    for venta in ventas_db:
        imagen_cover = None
        nombres_productos = []

        for detalle in venta.detalles:
            nombres_productos.append(detalle.nombre_producto_snapshot)
            
            # Buscar la primera imagen disponible del primer stock
            if not imagen_cover and detalle.stock and detalle.stock.variante and detalle.stock.variante.imagenes:
                imgs = sorted(detalle.stock.variante.imagenes, key=lambda x: x.orden or 0)
                if imgs:
                    imagen_cover = imgs[0].url

        # Resumen de productos bonito
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

    # 5. RETORNO FINAL
    return {
        "total": total_count,
        "items": resultados,
        "suma_recaudado": float(total_recaudado),
        "suma_beneficio": float(total_beneficio)
    }