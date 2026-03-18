# app/models/item_venta_model.py
from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

# app/models/item_venta_model.py

class Stock(Base):
    __tablename__ = "stocks" # Plural para la tabla
    
    id = Column(Integer, primary_key=True)
    variante_id = Column(Integer, ForeignKey("variantes.id", ondelete="CASCADE"))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=True)
    activo = Column(Boolean, default=True)
    etiqueta = Column(String(100)) # Ej: "Talla M", "256GB"
    fecha_compra = Column(Date, nullable=True)
    sku = Column(String(100), unique=True, index=True)
    orden = Column(Integer, default=0)
    cantidad = Column(Integer, default=0) 
    precio_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    descuento = Column(Float, default=0.0)
    publicar_web = Column(Boolean, default=False)
    publicar_vinted = Column(Boolean, default=False)
    publicar_wallapop = Column(Boolean, default=False)
    
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    # --- RELACIONES ---
    # Relación directa con los valores de los atributos (EAV)
    valores = relationship("ValorAtributo", back_populates="stock", cascade="all, delete-orphan")
    
    # Relación con su variante padre (Color)
    variante = relationship("Variante", back_populates="stocks")
    
    # Relación con el proveedor
    proveedor = relationship("Proveedor", back_populates="stocks")
