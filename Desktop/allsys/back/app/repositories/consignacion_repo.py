from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.stock_model import Stock
from app.models.ventas_model import DetalleVenta, Venta
from app.models.pagos_consignacion_model import PagoConsignacion
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.clientes_model import Cliente
from app.schemas.consignacion_schema import PagoCreate

# =====================================================
# 🧠 CEREBRO FINANCIERO: CÁLCULO DE COMISIONES
# =====================================================
# =====================================================
# 🧠 CEREBRO FINANCIERO: CÁLCULO DE COMISIONES
# =====================================================
def calcular_desglose_venta(
    precio_venta: float, 
    exento_gastos_gestion: bool = False, 
    donar_ganancias: bool = False  # ✨ NUEVO PARÁMETRO
) -> dict:
    """
    Calcula el desglose de comisiones. 
    - Si exento_gastos_gestion es True, la tarifa fija es 0.0€.
    - Si donar_ganancias es True, Allsys se queda el 100% y el cliente 0€.
    """
    # 🟢 CASO DONACIÓN DE GANANCIAS: El cliente cede su parte a Allsys
    if donar_ganancias:
        return {
            "precio_venta": float(precio_venta),
            "tarifa_fija": 0.0, # Irrelevante porque te lo quedas todo
            "porcentaje_aplicado": 100, # Allsys absorbe el 100%
            "comision_porcentaje_eur": float(precio_venta),
            "comision_total_allsys": float(precio_venta), # Beneficio total para ti
            "pago_cliente": 0.0 # El cliente no cobra nada
        }

    # 🔵 CASO NORMAL / VIP
    tarifa_fija = 0.0 if exento_gastos_gestion else 1.50
    
    if precio_venta <= 15.00:
        porcentaje = 0.50
    elif precio_venta <= 50.00:
        porcentaje = 0.40
    else:
        porcentaje = 0.30

    comision_porcentaje_eur = precio_venta * porcentaje
    comision_total_allsys = tarifa_fija + comision_porcentaje_eur
    pago_cliente = max(0.0, precio_venta - comision_total_allsys)
    
    return {
        "precio_venta": float(precio_venta),
        "tarifa_fija": float(tarifa_fija),
        "porcentaje_aplicado": int(porcentaje * 100), 
        "comision_porcentaje_eur": float(comision_porcentaje_eur),
        "comision_total_allsys": float(comision_total_allsys),
        "pago_cliente": float(pago_cliente)
    }

# =====================================================
# 📊 ESTADÍSTICAS GLOBALES DEL CLIENTE
# =====================================================
def obtener_estadisticas_cliente(db: Session, cliente_id: int):
    # Obtener el perfil del cliente para verificar el flag VIP
    cliente_db = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    exento_gestion = getattr(cliente_db, 'exento_gastos_gestion', False)

    stocks_del_cliente = db.query(Stock).filter(Stock.propietario_id == cliente_id).all()
    
    # Clasificación por estados
    prendas_en_stock = [s for s in stocks_del_cliente if getattr(s, 'estado_gestion', 'en_stock') == 'en_stock' and s.cantidad > 0]
    prendas_extraviadas = [s for s in stocks_del_cliente if getattr(s, 'estado_gestion', '') == 'extraviado']
    prendas_devueltas = [s for s in stocks_del_cliente if getattr(s, 'estado_gestion', '') == 'devuelto']
    prendas_donadas = [s for s in stocks_del_cliente if getattr(s, 'estado_gestion', '') == 'donado']
    
    # Ventas reales confirmadas
    detalles_vendidos = (
        db.query(DetalleVenta)
        .join(Stock, DetalleVenta.stock_id == Stock.id)
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .filter(Stock.propietario_id == cliente_id)
        .filter(Venta.estado_venta.in_(["procesando", "completada", "enviado", "entregado"]))
        .all()
    )
    
    prendas_vendidas = sum(d.cantidad for d in detalles_vendidos)
    dinero_generado = sum(d.precio_unitario_en_venta * d.cantidad for d in detalles_vendidos)
    
    # Cálculos acumulados
    dinero_para_cliente = 0.0
    
    # A. Sumar lo ganado en ventas (Respetando el flag VIP)
    for d in detalles_vendidos:
        pago_unitario = calcular_desglose_venta(d.precio_unitario_en_venta, exento_gastos_gestion=exento_gestion)["pago_cliente"]
        dinero_para_cliente += pago_unitario * d.cantidad

    # B. Sumar indemnización por extravíos
    for s in prendas_extraviadas:
        pago_extravio = calcular_desglose_venta(s.precio_venta, exento_gastos_gestion=exento_gestion)["pago_cliente"]
        dinero_para_cliente += pago_extravio

    # C. Restar tarifa de gestión por devoluciones (0€ si es familiar)
    tarifa_unit_dev = 0.0 if exento_gestion else 1.50
    deuda_por_devoluciones = len(prendas_devueltas) * tarifa_unit_dev
    dinero_para_cliente -= deuda_por_devoluciones
    
    # D. Beneficio Allsys
    beneficio_plataforma = dinero_generado - dinero_para_cliente
    
    # E. Pagos realizados
    pagos_realizados = db.query(func.sum(PagoConsignacion.monto)).filter(PagoConsignacion.cliente_id == cliente_id).scalar() or 0.0
    
    return {
        "total_prendas_entregadas": len(stocks_del_cliente),
        "prendas_vendidas": prendas_vendidas,
        "prendas_en_stock": len(prendas_en_stock),
        "prendas_devueltas": len(prendas_devueltas),
        "prendas_donadas": len(prendas_donadas),
        "prendas_extraviadas": len(prendas_extraviadas),
        "exento_gastos_gestion": exento_gestion,
        "deuda_por_devoluciones": float(deuda_por_devoluciones),
        "dinero_generado_ventas": float(dinero_generado),
        "dinero_para_cliente": float(dinero_para_cliente),
        "beneficio_plataforma": float(beneficio_plataforma),
        "dinero_ya_pagado": float(pagos_realizados),
        "saldo_pendiente": float(dinero_para_cliente - pagos_realizados)
    }

# =====================================================
# 📋 LISTADO PAGINADO DE PRENDAS
# =====================================================
def listar_prendas_detalle_cliente(db: Session, cliente_id: int, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    
    # Verificar flag VIP
    cliente_db = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    exento_gestion = getattr(cliente_db, 'exento_gastos_gestion', False)

    total_prendas = db.query(Stock).filter(Stock.propietario_id == cliente_id).count()

    stocks = (
        db.query(Stock)
        .options(
            joinedload(Stock.variante).joinedload(Variante.producto),
            joinedload(Stock.variante).joinedload(Variante.imagenes)
        )
        .filter(Stock.propietario_id == cliente_id)
        .order_by(Stock.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    stock_ids = [s.id for s in stocks]
    ventas_dict = {}
    if stock_ids:
        ventas = (
            db.query(DetalleVenta, Venta)
            .join(Venta, DetalleVenta.venta_id == Venta.id)
            .filter(DetalleVenta.stock_id.in_(stock_ids))
            .filter(Venta.estado_venta.in_(["procesando", "completada", "enviado", "entregado"]))
            .all()
        )
        ventas_dict = {detalle.stock_id: (detalle, venta) for detalle, venta in ventas}

    resultados = []
    for s in stocks:
        producto = s.variante.producto
        imagen_url = None
        if s.variante.imagenes:
            img_sorted = sorted(s.variante.imagenes, key=lambda x: x.orden or 0)
            if img_sorted: imagen_url = img_sorted[0].url

        estado_actual = getattr(s, 'estado_gestion', 'en_stock')

        if s.id in ventas_dict:
            detalle, venta = ventas_dict[s.id]
            estado = "vendida"
            fecha_v = venta.fecha
            desglose = calcular_desglose_venta(detalle.precio_unitario_en_venta, exento_gastos_gestion=exento_gestion)
        else:
            estado = estado_actual
            fecha_v = getattr(s, 'fecha_resolucion', None)
            
            if estado == "devuelto":
                coste_dev = 0.0 if exento_gestion else 1.50
                desglose = {
                    "precio_venta": 0.0,
                    "tarifa_fija": coste_dev,
                    "porcentaje_aplicado": 0,
                    "comision_porcentaje_eur": 0.0,
                    "comision_total_allsys": coste_dev,
                    "pago_cliente": -coste_dev
                }
            elif estado == "donado":
                desglose = {"precio_venta": 0.0, "tarifa_fija": 0.0, "porcentaje_aplicado": 0, "comision_porcentaje_eur": 0.0, "comision_total_allsys": 0.0, "pago_cliente": 0.0}
            elif estado == "extraviado":
                desglose = calcular_desglose_venta(s.precio_venta, exento_gastos_gestion=exento_gestion)
            else:
                desglose = calcular_desglose_venta(s.precio_venta, exento_gastos_gestion=exento_gestion)

        resultados.append({
            "stock_id": s.id,
            "sku": s.sku,
            "nombre_producto": f"{producto.nombre} - {s.etiqueta}",
            "imagen": imagen_url,
            "estado": estado,
            "fecha_venta": fecha_v,
            "finanzas": desglose
        })

    return {
        "total": total_prendas,
        "page": page,
        "limit": limit,
        "items": resultados
    }

# =====================================================
# 💸 GESTIÓN DE PAGOS AL CLIENTE
# =====================================================
def registrar_pago(db: Session, cliente_id: int, data: PagoCreate):
    nuevo_pago = PagoConsignacion(cliente_id=cliente_id, **data.dict())
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

def listar_pagos(db: Session, cliente_id: int):
    return db.query(PagoConsignacion).filter(PagoConsignacion.cliente_id == cliente_id).order_by(PagoConsignacion.fecha.desc()).all()