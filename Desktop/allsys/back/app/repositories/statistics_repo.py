from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc, and_
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from datetime import datetime, timedelta

def obtener_metricas_avanzadas(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    # 1. Filtros de tiempo
    filtros = []
    if fecha_inicio: filtros.append(Venta.fecha >= fecha_inicio)
    if fecha_fin: filtros.append(Venta.fecha <= f"{fecha_fin} 23:59:59")

    # --- A. KPIs GLOBALES (Los números grandes) ---
    # Calculamos: Ingresos, Costo Total de lo vendido, Cantidad de Ventas y Tickets
    query_base = db.query(
        func.count(Venta.id).label("total_operaciones"),
        func.sum(Venta.total).label("ingresos_brutos"),
        func.sum(Venta.costo_envio).label("total_envios"),
        func.sum(Venta.descuento_total).label("total_descuentos")
    ).filter(*filtros).first()

    # Cálculo del costo de mercadería vendida (COGS) para el periodo
    costo_mercaderia = db.query(
        func.sum(DetalleVenta.cantidad * Stock.precio_compra)
    ).join(Venta, DetalleVenta.venta_id == Venta.id)\
     .join(Stock, DetalleVenta.stock_id == Stock.id)\
     .filter(*filtros).scalar() or 0

    ingresos = float(query_base.ingresos_brutos or 0)
    ventas_count = query_base.total_operaciones or 0
    beneficio_neto = ingresos - float(costo_mercaderia)

    # --- B. RENDIMIENTO POR VENDEDOR ---
    # ¿Quién trae más dinero y quién es más rentable?
    vendedores = db.query(
        Venta.vendedor,
        func.count(Venta.id).label("num_ventas"),
        func.sum(Venta.total).label("ventas_totales"),
        # Beneficio por vendedor
        (func.sum(Venta.total) - func.sum(
            db.query(func.sum(DetalleVenta.cantidad * Stock.precio_compra))
            .filter(DetalleVenta.venta_id == Venta.id)
            .join(Stock, DetalleVenta.stock_id == Stock.id)
            .correlate(Venta).as_scalar()
        )).label("beneficio_vendedor")
    ).filter(*filtros).group_by(Venta.vendedor).order_by(desc("ventas_totales")).all()

    # --- C. RENDIMIENTO POR CANAL (Vinted, Web, Tienda) ---
    canales = db.query(
        Venta.canal,
        func.count(Venta.id).label("cantidad"),
        func.sum(Venta.total).label("total_canal")
    ).filter(*filtros).group_by(Venta.canal).all()

    # --- D. PRODUCTOS ESTRELLA (TOP 5) ---
    top_productos = db.query(
        DetalleVenta.nombre_producto_snapshot,
        func.sum(DetalleVenta.cantidad).label("vendidos"),
        func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario_en_venta).label("recaudado")
    ).join(Venta, DetalleVenta.venta_id == Venta.id)\
     .filter(*filtros)\
     .group_by(DetalleVenta.nombre_producto_snapshot)\
     .order_by(desc("vendidos")).limit(5).all()

    # --- E. MÉTRICAS AVANZADAS DE NEGOCIO ---
    ticket_promedio = ingresos / ventas_count if ventas_count > 0 else 0
    # ROI (Retorno de inversión): (Beneficio / Costo Inversión) * 100
    roi = (beneficio_neto / float(costo_mercaderia) * 100) if costo_mercaderia > 0 else 0

    return {
        "resumen": {
            "ingresos_brutos": ingresos,
            "beneficio_neto": beneficio_neto,
            "total_ventas": ventas_count,
            "ticket_promedio": ticket_promedio,
            "roi_periodo": f"{round(roi, 2)}%",
            "costo_mercaderia": float(costo_mercaderia)
        },
        "por_vendedor": [
            {"nombre": v.vendedor, "ventas": v.num_ventas, "total": float(v.ventas_totales), "lucro": float(v.beneficio_vendedor)} 
            for v in vendedores
        ],
        "por_canal": [
            {"canal": c.canal, "cantidad": c.cantidad, "total": float(c.total_canal)} 
            for c in canales
        ],
        "top_productos": [
            {"producto": p.nombre_producto_snapshot, "cantidad": p.vendidos, "total": float(p.recaudado)} 
            for p in top_productos
        ]
    }