from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from app.models.gastos_model import Gasto
from datetime import datetime, timedelta
from collections import defaultdict

def obtener_resumen_financiero(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    # 1. Preparar filtros
    filtros_venta = []
    filtros_gasto = []
    
    if fecha_inicio:
        filtros_venta.append(Venta.fecha >= fecha_inicio)
        filtros_gasto.append(Gasto.fecha >= fecha_inicio)
    if fecha_fin:
        # Aseguramos que cubra todo el día hasta el último segundo
        fecha_fin_full = f"{fecha_fin} 23:59:59"
        filtros_venta.append(Venta.fecha <= fecha_fin_full)
        filtros_gasto.append(Gasto.fecha <= fecha_fin_full)

    # 2. Cálculos de Ingresos y Gastos Operativos
    ingresos = db.query(func.sum(Venta.total)).filter(*filtros_venta).scalar() or 0
    gastos_ops = db.query(func.sum(Gasto.monto)).filter(*filtros_gasto).scalar() or 0
    
    # 3. COGS (Costo de lo Vendido)
    # Lo que te costó a ti la ropa que ya se vendió
    costo_vendido = db.query(func.sum(Stock.precio_compra * DetalleVenta.cantidad))\
        .join(DetalleVenta, Stock.id == DetalleVenta.stock_id)\
        .join(Venta, Venta.id == DetalleVenta.venta_id)\
        .filter(*filtros_venta).scalar() or 0
        
    # 4. Inversión en Stock Actual (Valor de lo que hay en estantes hoy)
    inversion_stock = db.query(func.sum(Stock.precio_compra * Stock.cantidad)).scalar() or 0

    # 5. LÓGICA FINANCIERA CORREGIDA
    # Ganancia Real: Lo que ganaste por las ventas hechas menos tus gastos operativos.
    ganancia_real = float(ingresos) - float(costo_vendido) - float(gastos_ops)
    
    # Saldo Teórico Banco: Es el flujo de caja (Cash Flow). 
    # Dinero que entró (Ventas) - Dinero que salió (Gastos + Compra de TODO el stock)
    # Nota: Restamos 'costo_vendido' (lo que ya se fue) e 'inversion_stock' (lo que pagaste y aún tienes).
    saldo_teorico = float(ingresos) - float(gastos_ops) - float(inversion_stock) - float(costo_vendido)

    return {
        "ingresos_totales": round(float(ingresos), 2),
        "gastos_operativos": round(float(gastos_ops), 2),
        "ganancia_real": round(ganancia_real, 2),
        "inversion_en_stock": round(float(inversion_stock), 2),
        "saldo_teorico_banco": round(saldo_teorico, 2)
    }

def obtener_datos_grafica_mensual(db: Session):
    # Optimizamos: Una sola query para ventas y una para gastos de los últimos 6 meses
    hoy = datetime.now()
    hace_6_meses = hoy - timedelta(days=180)
    
    # Query Ventas
    ventas_query = db.query(
        extract('month', Venta.fecha).label('mes'),
        extract('year', Venta.fecha).label('anio'),
        func.sum(Venta.total)
    ).filter(Venta.fecha >= hace_6_meses).group_by('anio', 'mes').all()

    # Query Gastos
    gastos_query = db.query(
        extract('month', Gasto.fecha).label('mes'),
        extract('year', Gasto.fecha).label('anio'),
        func.sum(Gasto.monto)
    ).filter(Gasto.fecha >= hace_6_meses).group_by('anio', 'mes').all()

    # Mapear resultados para fácil acceso
    data_ventas = {(int(r[1]), int(r[0])): float(r[2]) for r in ventas_query}
    data_gastos = {(int(r[1]), int(r[0])): float(r[2]) for r in gastos_query}

    resultados = []
    # Generar los últimos 6 meses (incluyendo el actual)
    for i in range(5, -1, -1):
        # Cálculo manual de meses para retroceder correctamente
        fecha_target = hoy.replace(day=1) - timedelta(days=i*30)
        m = fecha_target.month
        a = fecha_target.year
        
        resultados.append({
            "mes": fecha_target.strftime("%b"), # Ej: "Jan", "Feb"
            "ventas": data_ventas.get((a, m), 0.0),
            "gastos": data_gastos.get((a, m), 0.0)
        })
        
    return resultados