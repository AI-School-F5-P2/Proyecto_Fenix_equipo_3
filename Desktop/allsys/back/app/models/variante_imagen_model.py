from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

# app/models/variante_imagen_model.py
class Imagen(Base):
    __tablename__ = "imagenes_variante" # Asegúrate de que este nombre sea el que usas
    id = Column(Integer, primary_key=True)
    url = Column(String(500), nullable=False)
    
    # Debe apuntar a 'variantes.id'
    variante_id = Column(Integer, ForeignKey("variantes.id", ondelete="CASCADE"))
    
    # El back_populates debe coincidir con el nombre en la clase Variante
    variante = relationship("Variante", back_populates="imagenes")
    