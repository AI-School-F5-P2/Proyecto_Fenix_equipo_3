from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Imagen(Base):
    __tablename__ = "imagenes"
    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    variante_id = Column(Integer, ForeignKey("variantes.id"))

    variante = relationship("Variante", back_populates="imagenes")
    