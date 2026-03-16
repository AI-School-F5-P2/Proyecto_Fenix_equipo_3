from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base

# 1. EL CATÁLOGO (Ej: "Talla", "Material", "Contenido ML")
class Atributo(Base):
    __tablename__ = "atributos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    # Relación con todos los valores que existen de este tipo
    valores = relationship("ValorAtributo", back_populates="atributo", cascade="all, delete-orphan")

# 2. EL VALOR ESPECÍFICO (Ej: Stock #5 -> Atributo "Talla" -> Valor "XL")
class ValorAtributo(Base):
    __tablename__ = "valores_atributo"
    
    id = Column(Integer, primary_key=True)
    
    # Conexión al Stock (Lo que antes era ItemVenta)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    
    # Conexión al tipo de atributo
    atributo_id = Column(Integer, ForeignKey("atributos.id", ondelete="CASCADE"), nullable=False)
    
    # El valor real (Ej: "XL", "Algodón", "100")
    valor = Column(String(100), nullable=False)

    # Relaciones
    stock = relationship("Stock", back_populates="valores")
    atributo = relationship("Atributo", back_populates="valores")

    # Regla: No permitir que un mismo Stock tenga dos veces el mismo Atributo (Ej: No dos tallas)
    __table_args__ = (
        UniqueConstraint("stock_id", "atributo_id", name="uq_stock_atributo"),
    )