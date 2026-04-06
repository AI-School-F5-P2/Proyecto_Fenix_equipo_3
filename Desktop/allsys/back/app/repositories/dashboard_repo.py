from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from app.models.gastos_model import Gasto
from datetime import datetime, timedelta

def obtener_resumen_financiero(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    # Filtros base
    filtros_venta = []
    filtros_gasto = []
    
    if fecha_inicio:
        filtros_venta.append(Venta.fecha >= fecha_inicio)
        filtros_gasto.append(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        filtros_venta.append(Venta.fecha <= f"{fecha_fin} 23:59:59")
        filtros_gasto.append(Gasto.fecha <= f"{fecha_fin} 23:59:59")

    # 1. Ingresos (Ventas)
    ingresos = db.query(func.sum(Venta.total)).filter(*filtros_venta).scalar() or 0
    
    # 2. Gastos Operativos
    gastos_ops = db.query(func.sum(Gasto.monto)).filter(*filtros_gasto).scalar() or 0
    
    # 3. Costo de lo Vendido (COGS) -> Para calcular ganancia real
    costo_vendido = db.query(func.sum(Stock.precio_compra * DetalleVenta.cantidad))\
        .join(DetalleVenta, Stock.id == DetalleVenta.stock_id)\
        .join(Venta, Venta.id == DetalleVenta.venta_id)\
        .filter(*filtros_venta).scalar() or 0
        
    # 4. Inversión en Stock (Valor total de la mercadería actual en estantes)
    # Se calcula sumando precio_compra * cantidad de lo que hay hoy
    inversion_stock = db.query(func.sum(Stock.precio_compra * Stock.cantidad)).scalar() or 0

    # CALCULOS FINALES
    ganancia_real = float(ingresos) - float(costo_vendido) - float(gastos_ops)
    # El saldo teórico es: Ventas - Gastos - Inversión (porque el dinero de la ropa ya salió)
    saldo_teorico = float(ingresos) - float(gastos_ops) - float(inversion_stock)

    # ✨ IMPORTANTE: Estos nombres deben ser iguales a los del HTML en Angular
    return {
        "ingresos_totales": float(ingresos),
        "gastos_operativos": float(gastos_ops),
        "ganancia_real": ganancia_real,
        "inversion_en_stock": float(inversion_stock), # Antes decía 'inversion_en_percheros'
        "saldo_teorico_banco": saldo_teorico         # Antes faltaba esta key
    }

def obtener_datos_grafica_mensual(db: Session):
    hoy = datetime.now()
    resultados = []
    for i in range(5, -1, -1):
        fecha_obj = hoy - timedelta(days=i*30)
        mes = fecha_obj.month
        anio = fecha_obj.year
        v_mes = db.query(func.sum(Venta.total)).filter(extract('month', Venta.fecha) == mes, extract('year', Venta.fecha) == anio).scalar() or 0
        g_mes = db.query(func.sum(Gasto.monto)).filter(extract('month', Gasto.fecha) == mes, extract('year', Gasto.fecha) == anio).scalar() or 0
        resultados.append({
            "mes": fecha_obj.strftime("%b"),
            "ventas": float(v_mes),
            "gastos": float(g_mes)
        })
    return resultados

# def obtener_datos_grafica_mensual(db: Session):
#     # Obtenemos datos de los últimos 6 meses
#     hoy = datetime.now()
#     resultados = []
    
#     for i in range(5, -1, -1):
#         fecha_obj = hoy - timedelta(days=i*30)
#         mes = fecha_obj.month
#         anio = fecha_obj.year
        
#         v_mes = db.query(func.sum(Venta.total)).filter(
#             extract('month', Venta.fecha) == mes, 
#             extract('year', Venta.fecha) == anio
#         ).scalar() or 0
        
#         g_mes = db.query(func.sum(Gasto.monto)).filter(
#             extract('month', Gasto.fecha) == mes, 
#             extract('year', Gasto.fecha) == anio
#         ).scalar() or 0
        
#         resultados.append({
#             "mes": fecha_obj.strftime("%b"),
#             "ventas": float(v_mes),
#             "gastos": float(g_mes)
#         })
        
#     return resultados