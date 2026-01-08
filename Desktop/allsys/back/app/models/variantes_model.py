# app/models/variante_model.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Variante(Base):
    __tablename__ = "variantes"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="CASCADE"))

    sku = Column(String(100), unique=True, index=True, nullable=False)

    color = Column(String(20), nullable=False)
    color_nombre = Column(String(50), nullable=False)  # ✅ NUEVO
    precio = Column(Float, nullable=True)
    descuento = Column(Float, nullable=True)

    producto = relationship("Producto", back_populates="variantes")
    tallas = relationship("Talla", back_populates="variante", cascade="all, delete-orphan")
    imagenes = relationship("Imagen", back_populates="variante", cascade="all, delete-orphan")
