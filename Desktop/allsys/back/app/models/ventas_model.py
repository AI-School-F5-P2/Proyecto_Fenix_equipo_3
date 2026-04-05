from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    codigo_venta = Column(String(50), unique=True, nullable=False) 
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # --- FINANZAS DETALLADAS ---
    subtotal = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0.0) # Para contabilidad
    descuento_total = Column(Float, default=0.0)
    costo_envio = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    moneda = Column(String(10), default="EUR") # Por si acaso vendes en otras monedas

    # --- PAGOS Y SEGURIDAD ---
    metodo_pago = Column(String(50), nullable=False) 
    estado_pago = Column(String(50), default="pagado") 
    # Clave para Stripe, PayPal o ID de pedido de Vinted/Wallapop
    transaccion_id_externo = Column(String(100), nullable=True)

    # --- FLUJO DE TRABAJO ---
    # procesando, enviada, completada, cancelada, devuelta
    estado_venta = Column(String(50), default="completada") 
    canal = Column(String(50), nullable=False) # web, tienda, vinted, etc.
    vendedor = Column(String(50), nullable=False) 

    # --- CLIENTE ---
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) 
    nombre_cliente = Column(String(100), nullable=True)
    email_cliente = Column(String(100), nullable=True)
    notas_internas = Column(Text, nullable=True) # Para Yenny/Maikol

    # --- LOGÍSTICA ---
    estado_envio = Column(String(50), default="entregado") 
    direccion_envio = Column(Text, nullable=True)
    empresa_transporte = Column(String(50), nullable=True) 
    numero_seguimiento = Column(String(100), nullable=True)

    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")


class DetalleVenta(Base):
    __tablename__ = "detalles_venta"
    
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True) # Nullable por si borras el stock
    
    cantidad = Column(Integer, nullable=False)
    precio_unitario_en_venta = Column(Float, nullable=False) # El precio del momento
    
    # 🛡️ SEGURO DE DATOS: Si borras el stock, la factura sigue teniendo info
    nombre_producto_snapshot = Column(String(200)) 
    talla_snapshot = Column(String(50))
    color_snapshot = Column(String(50))

    venta = relationship("Venta", back_populates="detalles")
    stock = relationship("Stock")