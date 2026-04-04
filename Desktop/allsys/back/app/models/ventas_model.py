from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    # Identificador único visual para el cliente (Ej: VEN-10293)
    codigo_venta = Column(String(50), unique=True, nullable=False) 
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # ---------------- 1. DATOS FINANCIEROS ----------------
    subtotal = Column(Float, nullable=False, default=0.0) # Suma de productos sin envío ni descuentos
    descuento_aplicado = Column(Float, default=0.0)
    costo_envio = Column(Float, default=0.0)
    total = Column(Float, nullable=False) # Lo que el cliente pagó realmente
    
    # efectivo, tarjeta, bizum, stripe, saldo_vinted, wallapay
    metodo_pago = Column(String(50), nullable=False) 
    # pendiente, pagado, cancelado, reembolsado
    estado_pago = Column(String(50), default="pagado") 

    # ---------------- 2. ORIGEN DE LA VENTA ----------------
    # web, tienda_fisica, vinted, wallapop, instagram
    canal = Column(String(50), nullable=False) 
    # yenny, maikol, paola, sistema_web
    vendedor = Column(String(50), nullable=False) 

    # ---------------- 3. DATOS DEL COMPRADOR ----------------
    # Si el que compra es un usuario registrado en tu web
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True) 
    
    # Datos en texto por si es una venta rápida en tienda o viene de Vinted (no tienen cuenta en tu web)
    nombre_cliente = Column(String(100), nullable=True)
    email_cliente = Column(String(100), nullable=True)
    telefono_cliente = Column(String(50), nullable=True)

    # ---------------- 4. DATOS DE LOGÍSTICA / ENVÍO ----------------
    # pendiente_envio, enviado, entregado, recogido_en_tienda
    estado_envio = Column(String(50), default="pendiente_envio") 
    direccion_envio = Column(Text, nullable=True)
    
    # Ej: Correos, InPost, Seur...
    empresa_transporte = Column(String(50), nullable=True) 
    numero_seguimiento = Column(String(100), nullable=True)
    url_etiqueta = Column(String(255), nullable=True) # Por si generas el PDF de envío en tu web

    # Relaciones
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    # usuario = relationship("Usuario", back_populates="compras") # Descomenta si tienes tabla usuarios


class DetalleVenta(Base):
    __tablename__ = "detalles_venta"
    
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"))
    stock_id = Column(Integer, ForeignKey("stocks.id")) 
    
    cantidad = Column(Integer, nullable=False)
    # Congelamos el precio al que se vendió en ESE momento (por si luego cambias el precio en el inventario)
    precio_unitario = Column(Float, nullable=False) 
    
    # Histórico visual para no perder el dato si el stock se borra un día
    nombre_producto_historico = Column(String(200), nullable=True) 
    talla_historica = Column(String(50), nullable=True)

    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    stock = relationship("Stock")