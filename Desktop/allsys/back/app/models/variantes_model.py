from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

# app/models/variantes_model.py

class Variante(Base):
    __tablename__ = "variantes"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))
    sku = Column(String(100), unique=True)
    activo = Column(Boolean, default=True)
    identidad_variante = Column(String(100))  # "Rojo", "Titanio", "Eau de Parfum", "Floral"
    hex_identidad = Column(String(50))     # El color para el Front (si aplica)
    ubicacion = Column(String(200))           # Estante, pasillo, etc.
    descripcion = Column(String(500))
    orden = Column(Integer, default=0)
    stocks = relationship("Stock", back_populates="variante", cascade="all, delete-orphan")
    imagenes = relationship("Imagen", back_populates="variante", cascade="all, delete-orphan")
    producto = relationship("Producto", back_populates="variantes")

#     identidad_variante: string; // Antes: valor_visual_nombre
#   hex_identidad: string; 