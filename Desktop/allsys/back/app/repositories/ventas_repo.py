from datetime import datetime
import random
import string
from sqlalchemy.orm import Session
from app.models.ventas_model import Venta, DetalleVenta
from app.models.stock_model import Stock
from fastapi import HTTPException

from app.schemas.ventas_schema import VentaCreate

def generar_codigo_venta():
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VEN-{rand}"

def registrar_venta(db: Session, data: VentaCreate):
    try:
        # 1. Calcular Totales
        subtotal = sum(d.cantidad * d.precio_unitario for d in data.detalles)
        total_final = (subtotal + data.costo_envio) - data.descuento_total

        # 2. Crear el objeto Venta (Padre)
        nueva_venta = Venta(
            codigo_venta=generar_codigo_venta(),
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