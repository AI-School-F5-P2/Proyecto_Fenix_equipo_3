import traceback

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

# Importaciones de todos los modelos necesarios según la arquitectura EAV
from app.models.proveedores_model import Proveedor
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from app.models.variantes_model import Variante
from app.models.gastos_model import Gasto
from app.models.producto_model import Producto
from app.models.categorias_model import Categoria

def obtener_inteligencia_negocio(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    # ==========================================
    # 1. PREPARACIÓN DE FILTROS BASE
    # ==========================================
    # Filtramos ventas por estado para asegurar ingresos reales
    f_ventas = [Venta.estado_venta.in_(["completada", "enviada", "procesando"])]
    f_gastos = []
    f_stock_nuevo = [] # Para medir lo que entró a la tienda en este periodo

    if fecha_inicio:
        f_ventas.append(Venta.fecha >= fecha_inicio)
        f_gastos.append(Gasto.fecha >= fecha_inicio)
        f_stock_nuevo.append(Stock.fecha_registro >= fecha_inicio)
        
    if fecha_fin:
        fecha_fin_full = f"{fecha_fin} 23:59:59"
        f_ventas.append(Venta.fecha <= fecha_fin_full)
        f_gastos.append(Gasto.fecha <= fecha_fin_full)
        f_stock_nuevo.append(Stock.fecha_registro <= fecha_fin_full)

    # ==========================================
    # 2. CÁLCULO DE KPIs FINANCIEROS GLOBALES
    # ==========================================
    ingresos = db.query(func.sum(Venta.total)).filter(*f_ventas).scalar() or 0
    gastos_fijos = db.query(func.sum(Gasto.monto)).filter(*f_gastos).scalar() or 0
    total_ops = db.query(func.count(Venta.id)).filter(*f_ventas).scalar() or 0
    
    # Costo de lo Vendido (COGS): Lo que te costó la ropa que ya salió de la tienda
    costo_mercaderia_vendida = db.query(
        func.sum(DetalleVenta.cantidad * Stock.precio_compra)
    ).join(Venta, DetalleVenta.venta_id == Venta.id)\
     .join(Stock, DetalleVenta.stock_id == Stock.id)\
     .filter(*f_ventas).scalar() or 0

    # Beneficio Neto = Ventas - (Costo Ropa + Gastos)
    beneficio_neto = float(ingresos) - float(costo_mercaderia_vendida) - float(gastos_fijos)
    
    # ROI: Eficiencia de la inversión en la ropa vendida
    roi_valor = (beneficio_neto / float(costo_mercaderia_vendida) * 100) if costo_mercaderia_vendida > 0 else 0

    # ==========================================
    # 3. ANÁLISIS DE LIQUIDEZ Y STOCK REMANENTE
    # ==========================================
    # Dinero que sigue en perchas de lo comprado este mes
    remanente_dinero = db.query(
        func.sum(Stock.precio_compra * Stock.cantidad)
    ).filter(*f_stock_nuevo).scalar() or 0

    # Cantidad física de prendas que aún quedan de las nuevas entradas
    remanente_unidades = db.query(
        func.sum(Stock.cantidad)
    ).filter(*f_stock_nuevo).scalar() or 0

    # Inversión Total del periodo: Costo de lo vendido + Costo de lo que queda
    total_invertido_periodo = float(costo_mercaderia_vendida) + float(remanente_dinero)

    # ==========================================
    # 4. DIMENSIONES PARA GRÁFICAS
    # ==========================================
    # Rendimiento por vendedor
    vendedores = db.query(
        Venta.vendedor, 
        func.sum(Venta.total)
    ).filter(*f_ventas).group_by(Venta.vendedor).order_by(desc(func.sum(Venta.total))).all()

    # Distribución de ingresos por canal de venta
    canales = db.query(
        Venta.canal, 
        func.sum(Venta.total)
    ).filter(*f_ventas).group_by(Venta.canal).all()

    # ==========================================
    # 5. TOP 5 CATEGORÍAS GANADORAS
    # ==========================================
    # El camino de Joins es: DetalleVenta -> Stock -> Variante -> Producto -> Categoria
    top_categorias = db.query(
        Categoria.nombre,
        func.sum(DetalleVenta.cantidad).label("total_cant")
    ).join(Venta, DetalleVenta.venta_id == Venta.id)\
     .join(Stock, DetalleVenta.stock_id == Stock.id)\
     .join(Variante, Stock.variante_id == Variante.id) \
     .join(Producto, Variante.producto_id == Producto.id) \
     .join(Categoria, Producto.categoria_id == Categoria.id)\
     .filter(*f_ventas)\
     .group_by(Categoria.nombre)\
     .order_by(desc("total_cant")).limit(5).all()

    # ==========================================
    # 6. CONSTRUCCIÓN DEL JSON DE RESPUESTA
    # ==========================================
    return {
        "global": {
            "ingresos": float(ingresos),
            "beneficio": float(beneficio_neto),
            "roi": f"{round(roi_valor, 2)}%",
            "ticket_medio": float(ingresos) / total_ops if total_ops > 0 else 0,
            "operaciones": int(total_ops),
            "total_invertido_mes": float(total_invertido_periodo),
            "stock_remanente_mes": float(remanente_dinero),
            "articulos_remanentes": int(remanente_unidades)
        },
        # Los 'if v[0]' previenen que un valor nulo rompa el frontend
        "vendedores": [{"nombre": v[0] if v[0] else "Desconocido", "total": float(v[1])} for v in vendedores],
        "canales": [{"nombre": c[0] if c[0] else "Sin Canal", "total": float(c[1])} for c in canales],
        "top_categorias": [{"nombre": cat[0] if cat[0] else "Sin Categoría", "cantidad": int(cat[1])} for cat in top_categorias]
    }


# =====================================================================
# NUEVO ENDPOINT: ANÁLISIS DE RENDIMIENTO DE COMPRAS (COHORTES)
# =====================================================================

def obtener_rendimiento_compras(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    # 1. Filtramos EXCLUSIVAMENTE por la fecha en la que la ropa entró a la tienda
    f_stock = []
    if fecha_inicio:
        f_stock.append(Stock.fecha_registro >= fecha_inicio)
    if fecha_fin:
        f_stock.append(Stock.fecha_registro <= f"{fecha_fin} 23:59:59")

    # Para las ventas, solo nos importan las que se cobraron (estado válido)
    f_ventas_validas = Venta.estado_venta.in_(["completada", "enviada", "procesando"])

    # --- A. LO QUE QUEDA EN TIENDA (EL REMANENTE) ---
    remanente_dinero = db.query(
        func.sum(Stock.precio_compra * Stock.cantidad)
    ).filter(*f_stock).scalar() or 0

    remanente_unidades = db.query(
        func.sum(Stock.cantidad)
    ).filter(*f_stock).scalar() or 0

    # --- B. LO QUE YA SE VENDIÓ DE ESTAS COMPRAS ---
    prendas_vendidas = db.query(
        func.sum(DetalleVenta.cantidad)
    ).join(Stock, DetalleVenta.stock_id == Stock.id)\
     .join(Venta, DetalleVenta.venta_id == Venta.id)\
     .filter(*f_stock, f_ventas_validas).scalar() or 0

    costo_recuperado = db.query(
        func.sum(DetalleVenta.cantidad * Stock.precio_compra)
    ).join(Stock, DetalleVenta.stock_id == Stock.id)\
     .join(Venta, DetalleVenta.venta_id == Venta.id)\
     .filter(*f_stock, f_ventas_validas).scalar() or 0

    # 🛡️ CORRECCIÓN APLICADA AQUÍ: Se usa precio_unitario_en_venta 
    ingresos_generados = db.query(
        func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario_en_venta) 
    ).join(Stock, DetalleVenta.stock_id == Stock.id)\
     .join(Venta, DetalleVenta.venta_id == Venta.id)\
     .filter(*f_stock, f_ventas_validas).scalar() or 0

    # --- C. CÁLCULOS FINALES DE LA INVERSIÓN ---
    inversion_total = float(remanente_dinero) + float(costo_recuperado)
    unidades_compradas = int(remanente_unidades) + int(prendas_vendidas)

    beneficio_inversion = float(ingresos_generados) - inversion_total

    # Retorno de Inversión (ROI) de este periodo de compras
    roi_inversion = (beneficio_inversion / inversion_total * 100) if inversion_total > 0 else 0

    return {
        "analisis_inversion": {
            "inversion_total": inversion_total,
            "prendas_compradas": unidades_compradas,
            "ingresos_generados": float(ingresos_generados),
            "beneficio_inversion": beneficio_inversion,
            "roi_inversion": f"{round(roi_inversion, 2)}%",
            "remanente_dinero": float(remanente_dinero),
            "prendas_atrapadas": int(remanente_unidades),
            "prendas_vendidas": int(prendas_vendidas),
            "tasa_venta": f"{round((prendas_vendidas / unidades_compradas * 100), 2)}%" if unidades_compradas > 0 else "0%"
        }
    }





# =====================================================================
# NUEVO ENDPOINT: ANÁLISIS DE RENDIMIENTO POR PROVEEDORES
# =====================================================================

# =====================================================================
# NUEVO ENDPOINT: ANÁLISIS DE RENDIMIENTO POR PROVEEDORES
# =====================================================================
def obtener_rendimiento_proveedores(db: Session, fecha_inicio: str = None, fecha_fin: str = None):
    try:
        # 1. Detector Dinámico de Columna: Buscamos cómo se llama la columna de texto del Proveedor
        if hasattr(Proveedor, 'nombre'):
            col_prov_nombre = Proveedor.nombre
        elif hasattr(Proveedor, 'empresa'):
            col_prov_nombre = Proveedor.empresa
        elif hasattr(Proveedor, 'razon_social'):
            col_prov_nombre = Proveedor.razon_social
        else:
            col_prov_nombre = Proveedor.id # Fallback de seguridad extremo

        # 2. Filtros de Fechas
        f_stock = []
        if fecha_inicio:
            f_stock.append(Stock.fecha_registro >= fecha_inicio)
        if fecha_fin:
            f_stock.append(Stock.fecha_registro <= f"{fecha_fin} 23:59:59")

        # Concatenación segura de filtros para la venta
        filtros_ventas = f_stock.copy()
        filtros_ventas.append(Venta.estado_venta.in_(["completada", "enviada", "procesando"]))

        # --- A. LO QUE QUEDA EN TIENDA ---
        stock_query = db.query(
            col_prov_nombre.label("proveedor"),
            func.sum(Stock.precio_compra * Stock.cantidad).label("remanente_dinero"),
            func.sum(Stock.cantidad).label("remanente_unidades")
        ).select_from(Stock)\
         .outerjoin(Proveedor, Stock.proveedor_id == Proveedor.id)\
         .filter(*f_stock)\
         .group_by(col_prov_nombre).all()

        # --- B. LO QUE YA SE VENDIÓ ---
        ventas_query = db.query(
            col_prov_nombre.label("proveedor"),
            func.sum(DetalleVenta.cantidad).label("prendas_vendidas"),
            func.sum(DetalleVenta.cantidad * Stock.precio_compra).label("costo_recuperado"),
            func.sum(DetalleVenta.cantidad * DetalleVenta.precio_unitario_en_venta).label("ingresos_generados")
        ).select_from(DetalleVenta)\
         .join(Stock, DetalleVenta.stock_id == Stock.id)\
         .join(Venta, DetalleVenta.venta_id == Venta.id)\
         .outerjoin(Proveedor, Stock.proveedor_id == Proveedor.id)\
         .filter(*filtros_ventas)\
         .group_by(col_prov_nombre).all()

        # --- C. CONSOLIDAR LOS DATOS ---
        proveedores_stats = {}

        for s in stock_query:
            prov = str(s.proveedor) if s.proveedor else "Sin Proveedor"
            proveedores_stats[prov] = {
                "nombre": prov,
                "remanente_dinero": float(s.remanente_dinero or 0),
                "remanente_unidades": int(s.remanente_unidades or 0),
                "prendas_vendidas": 0,
                "costo_recuperado": 0.0,
                "ingresos_generados": 0.0
            }

        for v in ventas_query:
            prov = str(v.proveedor) if v.proveedor else "Sin Proveedor"
            if prov not in proveedores_stats:
                proveedores_stats[prov] = {
                    "nombre": prov,
                    "remanente_dinero": 0.0,
                    "remanente_unidades": 0,
                    "prendas_vendidas": 0,
                    "costo_recuperado": 0.0,
                    "ingresos_generados": 0.0
                }
            proveedores_stats[prov]["prendas_vendidas"] = int(v.prendas_vendidas or 0)
            proveedores_stats[prov]["costo_recuperado"] = float(v.costo_recuperado or 0)
            proveedores_stats[prov]["ingresos_generados"] = float(v.ingresos_generados or 0)

        # --- D. CÁLCULOS DE RENTABILIDAD FINAL ---
        resultados = []
        for prov, data in proveedores_stats.items():
            inv_total = data["remanente_dinero"] + data["costo_recuperado"]
            prendas_totales = data["remanente_unidades"] + data["prendas_vendidas"]
            
            beneficio = data["ingresos_generados"] - inv_total
            roi = (beneficio / inv_total * 100) if inv_total > 0 else 0
            tasa_venta = (data["prendas_vendidas"] / prendas_totales * 100) if prendas_totales > 0 else 0

            resultados.append({
                "nombre": data["nombre"],
                "inversion_total": inv_total,
                "prendas_compradas": prendas_totales,
                "ingresos_generados": data["ingresos_generados"],
                "beneficio": beneficio,
                "roi_pct": round(roi, 2),
                "remanente_dinero": data["remanente_dinero"],
                "prendas_atrapadas": data["remanente_unidades"],
                "prendas_vendidas": data["prendas_vendidas"],
                "tasa_venta_pct": round(tasa_venta, 2)
            })

        resultados.sort(key=lambda x: x["beneficio"], reverse=True)

        return {"ranking_proveedores": resultados}

    except Exception as e:
        # INTERCEPTOR DE ERRORES: Imprime el problema real en la consola
        print("\n\n================ 🚨 ERROR EN PROVEEDORES 🚨 ================")
        traceback.print_exc()
        print("============================================================\n\n")
        raise e