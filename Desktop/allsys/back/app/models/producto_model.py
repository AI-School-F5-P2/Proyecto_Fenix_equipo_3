from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500))
    tipo = Column(String(50)) # ropa, calzado, etc.
    estado = Column(String(50), default="nuevo")
    activo = Column(Boolean, default=True)
    publico_objetivo = Column(String(50)) 
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    sku = Column(String(100), unique=True)

    # Relaciones
    variantes = relationship("Variante", back_populates="producto", cascade="all, delete-orphan")
    categoria = relationship("Categoria")
    marca = relationship("Marca")