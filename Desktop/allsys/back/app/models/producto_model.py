from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=True)  # precio base opcional
    stock = Column(Integer, default=0)

    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))

    tipo = Column(String(50), nullable=False)  
    # ropa | calzado | accesorios | perfumes | tecnologia | electro | muebles

    categoria = relationship("Categoria", back_populates="productos")
    marca = relationship("Marca", back_populates="productos")
    variantes = relationship("Variante", back_populates="producto", cascade="all, delete-orphan")

    
