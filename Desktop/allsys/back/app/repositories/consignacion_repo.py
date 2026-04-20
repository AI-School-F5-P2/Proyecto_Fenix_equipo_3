from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.stock_model import Stock
from app.models.ventas_model import DetalleVenta, Venta
from app.models.pagos_consignacion_model import PagoConsignacion
from app.schemas.consignacion_schema import PagoCreate

def obtener_estadisticas_cliente(db: Session, cliente_id: int):
    # 1. Prendas en posesión del cliente
    stocks_del_cliente = db.query(Stock).filter(Stock.propietario_id == cliente_id).all()
    prendas_en_stock = sum(s.cantidad for s in stocks_del_cliente if s.activo)
    
    # 2. Ventas realizadas (Solo ventas que no estén canceladas)
    detalles_vendidos = (
        db.query(DetalleVenta)
        .join(Stock, DetalleVenta.stock_id == Stock.id)
        .join(Venta, DetalleVenta.venta_id == Venta.id)
        .filter(Stock.propietario_id == cliente_id)
        .filter(Venta.estado_venta.in_(["procesando", "completada", "enviado", "entregado"]))
        .all()
    )
    
    prendas_vendidas = sum(d.cantidad for d in detalles_vendidos)
    
    # 3. Dinero
    # Total vendido en las plataformas (Vinted/Web)
    dinero_generado = sum(d.precio_unitario_en_venta * d.cantidad for d in detalles_vendidos)
    
    # Usamos el precio_compra como la "Comisión Pactada" para el cliente
    dinero_para_cliente = sum(d.stock.precio_compra * d.cantidad for d in detalles_vendidos if d.stock)
    
    beneficio_plataforma = dinero_generado - dinero_para_cliente
    
    # 4. Pagos ya realizados al cliente
    pagos = db.query(func.sum(PagoConsignacion.monto)).filter(PagoConsignacion.cliente_id == cliente_id).scalar() or 0.0
    
    return {
        "total_prendas_entregadas": prendas_en_stock + prendas_vendidas,
        "prendas_vendidas": prendas_vendidas,
        "prendas_en_stock": prendas_en_stock,
        "dinero_generado_ventas": float(dinero_generado),
        "dinero_para_cliente": float(dinero_para_cliente),
        "beneficio_plataforma": float(beneficio_plataforma),
        "dinero_ya_pagado": float(pagos),
        "saldo_pendiente": float(dinero_para_cliente - pagos)
    }

def registrar_pago(db: Session, cliente_id: int, data: PagoCreate):
    nuevo_pago = PagoConsignacion(cliente_id=cliente_id, **data.dict())
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

def listar_pagos(db: Session, cliente_id: int):
    return db.query(PagoConsignacion).filter(PagoConsignacion.cliente_id == cliente_id).order_by(PagoConsignacion.fecha.desc()).all()