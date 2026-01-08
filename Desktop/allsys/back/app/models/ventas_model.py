from sqlalchemy import Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)

    vendedor = Column(String(50), nullable=False)  # <-- tamaño definido
    canal = Column(String(50), nullable=False)     # <-- tamaño definido
    comprador = Column(String(100), nullable=True) # <-- tamaño definido

    detalles = relationship(
        "DetalleVenta",
        back_populates="venta",
        cascade="all, delete"
    )


class DetalleVenta(Base):
    __tablename__ = "detalle_venta"

    id = Column(Integer, primary_key=True)

    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    variante_id = Column(Integer, ForeignKey("variantes.id"), nullable=False)
    talla_id = Column(Integer, ForeignKey("tallas.id"), nullable=False)

    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    variante = relationship("Variante")
    talla = relationship("Talla")
