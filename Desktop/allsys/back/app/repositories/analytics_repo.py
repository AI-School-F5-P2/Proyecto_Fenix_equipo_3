from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.ventas_model import Venta
from app.models.gastos_model import Gasto

def obtener_resumen_financiero(
    db: Session, 
    fecha_inicio: str = None, 
    fecha_fin: str = None,
    vendedor: str = None,
    canal: str = None
):
    # 1. Preparar consultas base
    query_ventas = db.query(Venta).filter(Venta.estado_venta.in_(["completada", "enviada", "procesando"]))
    query_gastos = db.query(Gasto)

    # 2. Aplicar filtros de fecha a AMBAS tablas
    if fecha_inicio:
        query_ventas = query_ventas.filter(Venta.fecha >= fecha_inicio)
        query_gastos = query_gastos.filter(Gasto.fecha >= fecha_inicio)
    
    if fecha_fin:
        query_ventas = query_ventas.filter(Venta.fecha <= f"{fecha_fin} 23:59:59")
        query_gastos = query_gastos.filter(Gasto.fecha <= f"{fecha_fin} 23:59:59")

    # 3. Filtros específicos de ventas (Vendedor y Canal)
    if vendedor:
        query_ventas = query_ventas.filter(Venta.vendedor == vendedor)
    if canal:
        query_ventas = query_ventas.filter(Venta.canal == canal)

    # 4. Calcular Totales usando SQL (sum)
    # scalar() devuelve el número directamente, si no hay nada devuelve None, por eso ponemos "or 0.0"
    total_ingresos = db.query(func.sum(query_ventas.subquery().c.total)).scalar() or 0.0
    
    # Si filtramos por vendedor o canal, NO restamos los gastos generales para no distorsionar 
    # (Maikol no paga el alquiler del local de sus ventas). 
    # Solo calculamos gastos si estamos viendo el global del negocio.
    if vendedor or canal:
        total_gastos = 0.0
    else:
        total_gastos = db.query(func.sum(query_gastos.subquery().c.monto)).scalar() or 0.0

    beneficio_neto = total_ingresos - total_gastos

    # 5. Desglose de ventas por Canal (Para saber qué plataforma da más dinero)
    ventas_por_canal = db.query(
        Venta.canal, func.sum(Venta.total).label('total')
    ).filter(Venta.estado_venta.in_(["completada", "enviada", "procesando"]))
    
    if fecha_inicio: ventas_por_canal = ventas_por_canal.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin: ventas_por_canal = ventas_por_canal.filter(Venta.fecha <= f"{fecha_fin} 23:59:59")
    
    ventas_por_canal = ventas_por_canal.group_by(Venta.canal).all()

    return {
        "resumen": {
            "ingresos": round(total_ingresos, 2),
            "gastos": round(total_gastos, 2),
            "beneficio": round(beneficio_neto, 2),
            "margen_ganancia": round((beneficio_neto / total_ingresos * 100), 2) if total_ingresos > 0 else 0
        },
        "desglose_canales": [{"canal": c[0], "total": round(c[1], 2)} for c in ventas_por_canal]
    }