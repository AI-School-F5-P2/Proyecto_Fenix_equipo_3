from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)  # subcategorías

    # Relaciones
    subcategorias = relationship("Categoria")  # relación consigo misma
    productos = relationship("Producto", back_populates="categoria", lazy="dynamic")
    


